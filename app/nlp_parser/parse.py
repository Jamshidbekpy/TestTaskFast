from fastapi import APIRouter, HTTPException, Depends
from nlp_parser.parser import EventParser
from nlp_parser.models import ParseRequest, ParseResponse
from app.dependencies import get_db
from app.models import AuditLog

router = APIRouter(prefix="/parse", tags=["parser"])

# Global parser instance
_parser = None

def get_parser():
    """Parser instance olish"""
    global _parser
    if _parser is None:
        _parser = EventParser()
    return _parser

@router.post("/", response_model=ParseResponse)
async def parse_prompt(
    request: ParseRequest,
    parser: EventParser = Depends(get_parser),
    db = Depends(get_db)
):
    """
    Promptni tahlil qilish
    
    - **prompt**: Event haqida matn (UZ/RU/EN)
    - **locale**: Til (optional, avtomatik aniqlanadi)
    - **user_timezone**: Foydalanuvchi vaqt mintaqasi
    - **user_id**: Foydalanuvchi ID (optional)
    
    Returns:
        Parsed event ma'lumotlari
    """
    try:
        response = parser.parse(request)
        
        # Audit log yozish
        if request.user_id:
            audit_log = AuditLog(
                user_id=request.user_id,
                action="PARSE_PROMPT",
                payload={
                    "prompt": request.prompt[:100],  # First 100 chars
                    "locale": request.locale.value if request.locale else None,
                    "success": response.success,
                    "intent": response.data.intent.value if response.data else None,
                    "confidence": response.data.confidence if response.data else None
                }
            )
            db.add(audit_log)
            db.commit()
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
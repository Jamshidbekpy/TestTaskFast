from fastapi import APIRouter, HTTPException
from typing import Optional
from uuid import UUID

from app.utils.fake_nlp import (
    FakeEventParser, FakeParseRequest, 
    FakeParseResponse, FakeLanguage
)

router = APIRouter(prefix="/fake-parse", tags=["Fake NLP Parser"])

# Global fake parser instance
_fake_parser = None

def get_fake_parser():
    """Fake parser instance olish"""
    global _fake_parser
    if _fake_parser is None:
        _fake_parser = FakeEventParser()
    return _fake_parser

@router.post("/", response_model=FakeParseResponse)
async def fake_parse(
    prompt: str,
    locale: Optional[str] = None,
    user_timezone: str = "Asia/Tashkent",
    user_id: Optional[UUID] = None
):
    """
    Fake parse endpoint - Haqiqiy NLP ishlatmaydi
    
    - **prompt**: Event haqida matn
    - **locale**: Til (uz, ru, en) - avtomatik aniqlanadi
    - **user_timezone**: Vaqt mintaqasi
    - **user_id**: Foydalanuvchi ID
    
    Returns:
        Tasavvuriy parse natijasi
    """
    try:
        parser = get_fake_parser()
        
        # Locale ni convert qilish
        lang_map = {
            'uz': FakeLanguage.UZBEK,
            'ru': FakeLanguage.RUSSIAN,
            'en': FakeLanguage.ENGLISH
        }
        fake_locale = lang_map.get(locale) if locale else None
        
        request = FakeParseRequest(
            prompt=prompt,
            locale=fake_locale,
            user_timezone=user_timezone,
            user_id=user_id
        )
        
        response = parser.parse(request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_fake_parser():
    """Fake parser test endpoint"""
    parser = get_fake_parser()
    
    test_prompts = [
        "Ertaga soat 10:00 da yig'ilish",
        "Create meeting tomorrow at 3pm",
        "Создай встречу на завтра"
    ]
    
    results = []
    for prompt in test_prompts:
        request = FakeParseRequest(prompt=prompt)
        response = parser.parse(request)
        
        if response.success:
            results.append({
                "prompt": prompt,
                "intent": response.data.intent.value,
                "title": response.data.title,
                "time_start": response.data.time_start.isoformat() if response.data.time_start else None
            })
    
    return {
        "message": "Fake parser is working!",
        "test_results": results,
        "status": "active"
    }
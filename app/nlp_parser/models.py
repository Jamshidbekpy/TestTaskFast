from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID

class Intent(str, Enum):
    """Intent turlari"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SHOW = "show"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    UNKNOWN = "unknown"

class Language(str, Enum):
    """Qo'llab-quvvatlanadigan tillar"""
    UZBEK = "uz"
    RUSSIAN = "ru"
    ENGLISH = "en"

class Slot(BaseModel):
    """Slot ma'lumotlari"""
    type: str
    value: str
    start: int
    end: int
    confidence: float = Field(ge=0.0, le=1.0)

class ParsedEvent(BaseModel):
    """Parser natijasi"""
    intent: Intent
    language: Language
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Slot qiymatlari
    title: Optional[str] = None
    all_day: bool = False
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    repeat: Optional[str] = None  # RRULE format
    invites: List[str] = Field(default_factory=list)
    alerts: List[str] = Field(default_factory=list)  # ISO duration format
    url: Optional[str] = None
    note: Optional[str] = None
    
    # Qo'shimcha ma'lumotlar
    raw_slots: List[Slot] = Field(default_factory=list)
    normalized_text: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    @validator('alerts')
    def validate_alerts(cls, v):
        """Alertlarni tekshirish"""
        for alert in v:
            if not alert.startswith('PT'):
                raise ValueError(f"Invalid ISO duration format: {alert}")
        return v
    
    @validator('invites')
    def validate_invites(cls, v):
        """Email manzillarini tekshirish"""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        for email in v:
            if not email_pattern.match(email):
                raise ValueError(f"Invalid email format: {email}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary formatga o'tkazish"""
        result = self.dict(exclude={'raw_slots', 'warnings'})
        if self.time_start:
            result['time_start'] = self.time_start.isoformat()
        if self.time_end:
            result['time_end'] = self.time_end.isoformat()
        return result

class ParseRequest(BaseModel):
    """Parser so'rovi"""
    prompt: str
    locale: Optional[Language] = None
    user_timezone: str = "Asia/Tashkent"
    user_id: Optional[UUID] = None

class ParseResponse(BaseModel):
    """Parser javobi"""
    success: bool
    data: Optional[ParsedEvent] = None
    error: Optional[str] = None
    processing_time: float
    model_version: str = "1.0.0"
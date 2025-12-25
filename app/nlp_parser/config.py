import os
from pathlib import Path
from typing import Dict, List, Any
from pydantic_settings import BaseSettings

class NLPSettings(BaseSettings):
    """NLP parser sozlamalari"""
    
    # Model yo'llari
    model_dir: str = "models/nlp"
    intent_model_path: str = "intent_model"
    ner_model_path: str = "ner_model"
    language_model_path: str = "language_model"
    
    # BERT model konfiguratsiyasi
    bert_model_name: str = "distilbert-base-multilingual-cased"
    max_length: int = 128
    batch_size: int = 32
    
    # Intentlar ro'yxati
    intents: List[str] = [
        "create",
        "update", 
        "delete",
        "show",
        "confirm",
        "cancel",
        "unknown"
    ]
    
    # Slot turlari
    slot_types: List[str] = [
        "O",  # Outside
        "B-DATETIME", "I-DATETIME",
        "B-DURATION", "I-DURATION",
        "B-ALLDAY", "I-ALLDAY",
        "B-REPEAT", "I-REPEAT",
        "B-ALERT", "I-ALERT",
        "B-INVITE", "I-INVITE",
        "B-TITLE", "I-TITLE",
        "B-URL", "I-URL",
        "B-NOTE", "I-NOTE"
    ]
    
    # Tillar
    supported_languages: List[str] = ["uz", "ru", "en"]
    default_language: str = "uz"
    
    # Timezone
    default_timezone: str = "Asia/Tashkent"
    
    # Regex patternlar
    email_pattern: str = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    url_pattern: str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    
    # Default qiymatlar
    default_duration_hours: int = 1
    default_alert_minutes: int = 10
    
    class Config:
        env_prefix = "NLP_"
        case_sensitive = False

settings = NLPSettings()
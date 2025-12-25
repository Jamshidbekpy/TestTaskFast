"""
Fake NLP Parser - Haqiqiy model ishlatmasdan tasavvuriy natijalar qaytaradi
Test va development uchun mo'ljallangan
"""

import re
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4, UUID
from enum import Enum

from pydantic import BaseModel, Field, validator

class FakeIntent(str, Enum):
    """Tasavvuriy intentlar"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SHOW = "show"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    UNKNOWN = "unknown"

class FakeLanguage(str, Enum):
    """Tillar"""
    UZBEK = "uz"
    RUSSIAN = "ru"
    ENGLISH = "en"

class FakeParseRequest(BaseModel):
    """So'rov modeli"""
    prompt: str
    locale: Optional[FakeLanguage] = None
    user_timezone: str = "Asia/Tashkent"
    user_id: Optional[UUID] = None

class FakeSlot(BaseModel):
    """Tasavvuriy slot"""
    type: str
    value: str
    start: int
    end: int
    confidence: float = Field(ge=0.0, le=1.0)

class FakeParsedEvent(BaseModel):
    """Tasavvuriy parse natijasi"""
    intent: FakeIntent
    language: FakeLanguage
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Slot qiymatlari
    title: Optional[str] = None
    all_day: bool = False
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    repeat: Optional[str] = None
    invites: List[str] = []
    alerts: List[str] = []
    url: Optional[str] = None
    note: Optional[str] = None
    
    # Qo'shimcha
    raw_slots: List[FakeSlot] = []
    normalized_text: Optional[str] = None
    warnings: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionaryga o'tkazish"""
        result = self.dict(exclude={'raw_slots', 'warnings'})
        if self.time_start:
            result['time_start'] = self.time_start.isoformat()
        if self.time_end:
            result['time_end'] = self.time_end.isoformat()
        return result

class FakeParseResponse(BaseModel):
    """Javob modeli"""
    success: bool
    data: Optional[FakeParsedEvent] = None
    error: Optional[str] = None
    processing_time: float
    model_version: str = "fake-1.0.0"


class FakeEventParser:
    """
    Tasavvuriy Event Parser
    Haqiqiy NLP ishlatmaydi, random yoki pattern-based natijalar qaytaradi
    """
    
    def __init__(self):
        self.timezone = "Asia/Tashkent"
        
        # Intent patternlari
        self.intent_patterns = {
            FakeIntent.CREATE: [
                r'\b(yarat|создай|create)\b',
                r'\b(qo\'sh|добавь|add)\b',
                r'\b(planla|запланируй|schedule)\b',
                r'\b(tayinla|назначь|appoint)\b'
            ],
            FakeIntent.UPDATE: [
                r'\b(o\'zgartir|измени|change)\b',
                r'\b(ko\'chir|передвинь|move)\b',
                r'\b(yangila|обнови|update)\b',
                r'\b(tahrir|редактируй|edit)\b'
            ],
            FakeIntent.DELETE: [
                r'\b(o\'chir|удали|delete)\b',
                r'\b(bekor qil|отмени|cancel)\b',
                r'\b(olib tash|убери|remove)\b'
            ],
            FakeIntent.SHOW: [
                r'\b(ko\'rsat|покажи|show)\b',
                r'\b(ro\'yxat|список|list)\b',
                r'\b(qidir|найди|find)\b'
            ]
        }
        
        # Til patternlari
        self.language_patterns = {
            FakeLanguage.UZBEK: [
                r'\b(ertaga|bugun|kecha|soat|daqiqa|kun|hafta|oy)\b',
                r'\b(yig\'ilish|uchrashuv|reja|vaqt)\b',
                r'[ʻ\'ʼ]'  # Uzbek maxsus belgilar
            ],
            FakeLanguage.RUSSIAN: [
                r'\b(завтра|сегодня|вчера|час|минута|день|неделя|месяц)\b',
                r'\b(встреча|собрание|план|время)\b',
                r'[а-яА-ЯёЁ]'  # Kirill harflari
            ],
            FakeLanguage.ENGLISH: [
                r'\b(tomorrow|today|yesterday|hour|minute|day|week|month)\b',
                r'\b(meeting|appointment|schedule|time)\b'
            ]
        }
        
        # Random titlelar
        self.random_titles = [
            "Jamoa yig'ilishi",
            "Loyiha bahosi",
            "Mijoz bilan uchrashuv",
            "Texnik ko'rib chiqish",
            "Muhokama sessiyasi",
            "Team Meeting",
            "Project Review",
            "Client Call",
            "Technical Discussion",
            "Planning Session",
            "Совещание команды",
            "Обзор проекта",
            "Встреча с клиентом",
            "Техническое обсуждение"
        ]
        
        # Random email manzillar
        self.random_emails = [
            "jamshidbekshodibekov2004@gmail.com",
            "jamshidbekdev04@gmailcom",
            "jamshidbekchess04@gmailcom",
            "michael.brown@demo.net",
            "jamshidbekshodibekov39@gmail.com",
            "jamshidbekshodibekov306@gmail.com",
        ]
    
    def parse(self, request: FakeParseRequest) -> FakeParseResponse:
        """
        Promptni tasavvuriy parse qilish
        
        Args:
            request: Parse so'rovi
            
        Returns:
            Tasavvuriy parse natijasi
        """
        import time
        start_time = time.time()
        
        try:
            prompt = request.prompt.strip()
            if not prompt:
                raise ValueError("Prompt bo'sh bo'lishi mumkin emas")
            
            # 1. Tilni aniqlash (pattern orqali)
            language = self._detect_language(prompt, request.locale)
            
            # 2. Intentni aniqlash (pattern orqali)
            intent, intent_confidence = self._detect_intent(prompt)
            
            # 3. Tasavvuriy slotlarni yaratish
            raw_slots = self._generate_fake_slots(prompt, language)
            
            # 4. Tasavvuriy event ma'lumotlarini yaratish
            event_data = self._generate_fake_event_data(prompt, language)
            
            # 5. Warnings yaratish
            warnings = self._generate_warnings(event_data)
            
            # 6. ParsedEvent yaratish
            parsed_event = FakeParsedEvent(
                intent=intent,
                language=language,
                confidence=intent_confidence * 0.95,  # Yuqori confidence
                
                title=event_data.get('title'),
                all_day=event_data.get('all_day', False),
                time_start=event_data.get('time_start'),
                time_end=event_data.get('time_end'),
                repeat=event_data.get('repeat'),
                invites=event_data.get('invites', []),
                alerts=event_data.get('alerts', []),
                url=event_data.get('url'),
                note=event_data.get('note'),
                
                raw_slots=raw_slots,
                normalized_text=self._normalize_text(prompt, language),
                warnings=warnings
            )
            
            processing_time = time.time() - start_time
            
            return FakeParseResponse(
                success=True,
                data=parsed_event,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return FakeParseResponse(
                success=False,
                error=f"Fake parse error: {str(e)}",
                processing_time=processing_time
            )
    
    def _detect_language(self, text: str, preferred: Optional[FakeLanguage] = None) -> FakeLanguage:
        """Tilni pattern orqali aniqlash"""
        if preferred:
            return preferred
        
        text_lower = text.lower()
        
        # Patternlar bo'yicha tekshirish
        scores = {lang: 0 for lang in FakeLanguage}
        
        for lang, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    scores[lang] += 1
        
        # Eng ko'p scoreli tilni qaytarish
        detected = max(scores.items(), key=lambda x: x[1])[0]
        
        # Agar hech qanday pattern topilmasa, random til
        if scores[detected] == 0:
            return random.choice(list(FakeLanguage))
        
        return detected
    
    def _detect_intent(self, text: str) -> Tuple[FakeIntent, float]:
        """Intentni pattern orqali aniqlash"""
        text_lower = text.lower()
        
        # Patternlar bo'yicha tekshirish
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Random confidence 0.7-0.95 orasida
                    confidence = random.uniform(0.7, 0.95)
                    return intent, confidence
        
        # Agar pattern topilmasa, CREATE yoki UNKNOWN
        if random.random() > 0.3:
            return FakeIntent.CREATE, random.uniform(0.6, 0.8)
        else:
            return FakeIntent.UNKNOWN, random.uniform(0.5, 0.7)
    
    def _generate_fake_slots(self, text: str, language: FakeLanguage) -> List[FakeSlot]:
        """Tasavvuriy slotlarni yaratish"""
        slots = []
        words = text.split()
        
        # Slot turlari
        slot_types = [
            "DATETIME", "DURATION", "ALLDAY", "REPEAT",
            "ALERT", "INVITE", "TITLE", "URL", "NOTE"
        ]
        
        # Har bir so'z uchun slot yaratish (ehtimollik bilan)
        position = 0
        for word in words:
            # 30% ehtimollik bilan slot yaratish
            if random.random() < 0.3 and len(word) > 2:
                slot_type = random.choice(slot_types)
                slot = FakeSlot(
                    type=slot_type,
                    value=word,
                    start=position,
                    end=position + len(word),
                    confidence=random.uniform(0.6, 0.9)
                )
                slots.append(slot)
            
            position += len(word) + 1  # Bo'sh joy uchun
        
        return slots
    
    def _generate_fake_event_data(self, text: str, language: FakeLanguage) -> Dict[str, Any]:
        """Tasavvuriy event ma'lumotlarini yaratish"""
        # Random tanlovlar
        all_day = random.random() < 0.2  # 20% ehtimollik bilan all_day
        
        # Vaqtlarni yaratish (hozirgi vaqtdan keyin)
        now = datetime.now()
        
        # Start time: bugundan 1-7 kun ichida
        days_offset = random.randint(0, 7)
        hours_offset = random.randint(8, 18)  # Ish vaqti oralig'ida
        minutes_offset = random.choice([0, 15, 30, 45])
        
        time_start = now.replace(
            hour=hours_offset,
            minute=minutes_offset,
            second=0,
            microsecond=0
        ) + timedelta(days=days_offset)
        
        # Duration: 30 daqiqa - 4 soat
        duration_hours = random.choice([0.5, 1, 1.5, 2, 2.5, 3, 4])
        time_end = time_start + timedelta(hours=duration_hours)
        
        # Agar all_day bo'lsa
        if all_day:
            time_start = time_start.replace(hour=0, minute=0)
            time_end = time_start + timedelta(days=1)
        
        # Title: promptdan yoki random
        title = self._extract_title(text) or random.choice(self.random_titles)
        
        # Repeat: 30% ehtimollik bilan
        repeat = None
        if random.random() < 0.3:
            repeat_options = [
                "RRULE:FREQ=DAILY",
                "RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR",
                "RRULE:FREQ=WEEKLY;BYDAY=TU,TH",
                "RRULE:FREQ=MONTHLY"
            ]
            repeat = random.choice(repeat_options)
        
        # Invites: 1-3 ta random email
        num_invites = random.randint(0, 3)
        invites = random.sample(self.random_emails, num_invites) if num_invites > 0 else []
        
        # Alerts: 0-2 ta alert
        num_alerts = random.randint(0, 2)
        alerts = []
        for _ in range(num_alerts):
            alert_times = ["PT10M", "PT30M", "PT1H", "PT2H", "P1D"] # 10 min, 30 min, 1 soat, 2 soat, 1 kuni
            alerts.append(random.choice(alert_times))
        
        # URL: 20% ehtimollik bilan
        url = None
        if random.random() < 0.2:
            url = f"https://meet.example.com/{uuid4().hex[:8]}"
        
        # Note: 40% ehtimollik bilan
        note = None
        if random.random() < 0.4:
            notes = [
                "Muhim yig'ilish, iltimos kech qolmang",
                "Texnik tafsilotlar muhokama qilinadi",
                "Hujjatlarni olib kelishni unutmang",
                "Important meeting, please don't be late",
                "Технические детали будут обсуждаться"
            ]
            note = random.choice(notes)
        
        return {
            'title': title,
            'all_day': all_day,
            'time_start': time_start,
            'time_end': time_end,
            'repeat': repeat,
            'invites': invites,
            'alerts': alerts,
            'url': url,
            'note': note
        }
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Textdan sarlavha ajratib olish (oddiy patternlar orqali)"""
        # Qo'shtirnoq ichidagi matn
        quote_match = re.search(r'[\'"]([^\'"]+)[\'"]', text)
        if quote_match:
            return quote_match.group(1).strip()
        
        # "title: " dan keyingi matn
        title_match = re.search(r'(nomi|title|название)\s*:?\s*([^,\.]+)', text, re.IGNORECASE)
        if title_match:
            return title_match.group(2).strip()
        
        # Katta harflar bilan boshlanadigan va uzun so'z
        words = text.split()
        for word in words:
            if (word[0].isupper() and len(word) > 3 and 
                not word.endswith(('.', ',', ':', ';'))):
                return word
        
        return None
    
    def _normalize_text(self, text: str, language: FakeLanguage) -> str:
        """Textni normalizatsiya qilish (tasavvuriy)"""
        # Oddiy normalizatsiya
        normalized = text.strip()
        
        # Language-specific qisqartmalar
        if language == FakeLanguage.UZBEK:
            replacements = {
                r'\bsaot\b': 'soat',
                r'\bdaq\b': 'daqiqa',
                r'\bygn\b': 'yig\'ilish'
            }
        elif language == FakeLanguage.RUSSIAN:
            replacements = {
                r'\bвстр\b': 'встреча',
                r'\bсовещ\b': 'совещание',
                r'\bчас\b': 'час'
            }
        else:
            replacements = {
                r'\bmtg\b': 'meeting',
                r'\bappt\b': 'appointment',
                r'\bsched\b': 'schedule'
            }
        
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _generate_warnings(self, event_data: Dict) -> List[str]:
        """Tasavvuriy warninglar yaratish"""
        warnings = []
        
        # 20% ehtimollik bilan warning qo'shish
        if random.random() < 0.2:
            warning_options = [
                "Vaqt konflikti aniqlandi",
                "Davomiylik odatdagidan uzun",
                "Takrorlanish qoidasi noaniq",
                "Time conflict detected",
                "Duration is longer than usual",
                "Recurrence rule is ambiguous",
                "Обнаружен конфликт времени",
                "Продолжительность дольше обычного"
            ]
            warnings.append(random.choice(warning_options))
        
        # Agar all_day va time_start/end noaniq bo'lsa
        if event_data.get('all_day') and event_data.get('time_start'):
            if event_data['time_start'].hour != 0:
                warnings.append("All-day event should start at midnight")
        
        return warnings


# Convenience functions
def create_fake_parser() -> FakeEventParser:
    """Fake parser yaratish"""
    return FakeEventParser()

def parse_text(text: str, language: str = None) -> Dict:
    """
    Textni parse qilish (quick function)
    
    Args:
        text: Parse qilinadigan text
        language: Til kodi (uz, ru, en)
    
    Returns:
        Dict: Parse natijasi
    """
    parser = FakeEventParser()
    
    # Language ni convert qilish
    lang_map = {
        'uz': FakeLanguage.UZBEK,
        'ru': FakeLanguage.RUSSIAN,
        'en': FakeLanguage.ENGLISH
    }
    
    locale = lang_map.get(language) if language else None
    
    request = FakeParseRequest(
        prompt=text,
        locale=locale
    )
    
    response = parser.parse(request)
    
    if response.success and response.data:
        return response.data.to_dict()
    else:
        return {"error": response.error}


# Test uchun
if __name__ == "__main__":
    # Test qilish
    parser = FakeEventParser()
    
    test_prompts = [
        "Ertaga 15:00 da 'Design sync' yig'ilishi, 1 soat, 30 daqiqa oldin eslat",
        "Создай встречу 'Демо' завтра с 15:30 до 16:00, напомни за 10 минут",
        "Create meeting 'Budget review' tomorrow 3pm-4pm, weekly repeat",
        "Bugun soat 10:00 da loyiha bahosi",
        "Запланируй собрание на следующей неделе",
        "Schedule a team meeting next Monday"
    ]
    
    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"Prompt: {prompt}")
        print('-'*60)
        
        request = FakeParseRequest(prompt=prompt)
        response = parser.parse(request)
        
        if response.success:
            data = response.data
            print(f"Intent: {data.intent.value}")
            print(f"Language: {data.language.value}")
            print(f"Confidence: {data.confidence:.2f}")
            print(f"Title: {data.title}")
            print(f"Time: {data.time_start} - {data.time_end}")
            print(f"All day: {data.all_day}")
            print(f"Repeat: {data.repeat}")
            print(f"Invites: {data.invites}")
            print(f"Alerts: {data.alerts}")
            print(f"URL: {data.url}")
            print(f"Note: {data.note}")
            print(f"Warnings: {data.warnings}")
        else:
            print(f"Error: {response.error}")
        
        print(f"Processing time: {response.processing_time:.3f}s")
import re
from typing import Dict, Tuple
from .config import settings
from .models import Language

class LanguageDetector:
    """Tilni avtomatik aniqlovchi"""
    
    def __init__(self):
        # Til belgilari lug'atlari
        self.language_patterns = {
            Language.UZBEK: {
                'keywords': [
                    'ertaga', 'bugun', 'kecha', 'hafta', 'oy', 'yil',
                    'soat', 'daqiqa', 'soniya', 'oldin', 'keyin',
                    'butun kun', 'har', 'takror', 'eslatma', 'taklif'
                ],
                'alphabet': re.compile(r'[ʻ\'ʼ‘’"`]'),  # Uzbek maxsus belgilari
                'chars': set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ʻʼ'")
            },
            Language.RUSSIAN: {
                'keywords': [
                    'завтра', 'сегодня', 'вчера', 'неделя', 'месяц', 'год',
                    'час', 'минута', 'секунда', 'напомни', 'пригласи',
                    'весь день', 'каждый', 'повтор', 'встреча'
                ],
                'alphabet': re.compile(r'[а-яА-ЯёЁ]'),
                'chars': set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
            },
            Language.ENGLISH: {
                'keywords': [
                    'tomorrow', 'today', 'yesterday', 'week', 'month', 'year',
                    'hour', 'minute', 'second', 'remind', 'invite',
                    'all day', 'every', 'repeat', 'meeting', 'event'
                ],
                'alphabet': re.compile(r'[a-zA-Z]'),
                'chars': set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            }
        }
        
    def detect(self, text: str) -> Tuple[Language, float]:
        """
        Matndan tilni aniqlash
        
        Args:
            text: Analiz qilinadigan matn
            
        Returns:
            Tuple: (til, ishonch darajasi)
        """
        text = text.lower().strip()
        if not text:
            return Language(settings.default_language), 0.0
        
        scores = {}
        total_chars = len(text)
        
        for lang, patterns in self.language_patterns.items():
            score = 0.0
            
            # Kalit so'zlar bo'yicha
            keyword_score = 0
            for keyword in patterns['keywords']:
                if keyword in text:
                    keyword_score += 1
            
            # Alfavit bo'yicha
            lang_chars = sum(1 for char in text if char in patterns['chars'])
            alphabet_score = lang_chars / total_chars if total_chars > 0 else 0
            
            # Kombinatsiya
            score = (keyword_score * 0.7 + alphabet_score * 0.3)
            scores[lang] = score
        
        # Eng yuqori balli til
        detected_lang = max(scores.items(), key=lambda x: x[1])
        
        # Ishontirish darajasini normalizatsiya qilish
        max_score = max(scores.values())
        confidence = detected_lang[1] / max_score if max_score > 0 else 0.5
        
        return Language(detected_lang[0]), confidence
    
    def detect_with_fallback(self, text: str, fallback: Language = None) -> Language:
        """Tilni aniqlash, agar aniqlanmasa fallback qaytarish"""
        if not text:
            return fallback or Language(settings.default_language)
        
        lang, confidence = self.detect(text)
        
        # Agar ishonch darajasi past bo'lsa, fallback dan foydalanish
        if confidence < 0.3:
            return fallback or Language(settings.default_language)
        
        return lang
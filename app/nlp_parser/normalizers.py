from datetime import datetime, timedelta
import re
from typing import Optional, Tuple, List, Dict, Any
from dateutil import parser as date_parser
import pytz
from rrule import rrulestr, rrule, WEEKLY, DAILY, MONTHLY, YEARLY
from iso8601 import parse_duration

from .config import settings
from .models import Language
from .exceptions import NormalizationError

class DateTimeNormalizer:
    """Vaqt va sanani normalizatsiya qilish"""
    
    def __init__(self, timezone: str = "Asia/Tashkent"):
        self.timezone = pytz.timezone(timezone)
        self.now = datetime.now(self.timezone)
        
        # Relative vaqt lug'atlari
        self.relative_terms = {
            Language.UZBEK: {
                'bugun': 0,
                'ertaga': 1,
                'undan keyingi kun': 2,
                'kecha': -1,
                'shu hafta': 'this_week',
                'keyingi hafta': 'next_week',
                'hafta oxiri': 'weekend',
                'ertalab': 'morning',
                'tush': 'afternoon',
                'kechqurun': 'evening',
                'tun': 'night'
            },
            Language.RUSSIAN: {
                'сегодня': 0,
                'завтра': 1,
                'послезавтра': 2,
                'вчера': -1,
                'на этой неделе': 'this_week',
                'на следующей неделе': 'next_week',
                'выходные': 'weekend',
                'утро': 'morning',
                'день': 'afternoon',
                'вечер': 'evening',
                'ночь': 'night'
            },
            Language.ENGLISH: {
                'today': 0,
                'tomorrow': 1,
                'day after tomorrow': 2,
                'yesterday': -1,
                'this week': 'this_week',
                'next week': 'next_week',
                'weekend': 'weekend',
                'morning': 'morning',
                'afternoon': 'afternoon',
                'evening': 'evening',
                'night': 'night'
            }
        }
        
        # Vaqt formatlari
        self.time_formats = [
            '%H:%M',
            '%I:%M %p',
            '%I%p',
            '%H.%M'
        ]
    
    def normalize(self, text: str, lang: Language) -> Optional[datetime]:
        """
        Sanani normalizatsiya qilish
        
        Args:
            text: Vaqt/sana matni
            lang: Til
            
        Returns:
            datetime: Normalizatsiya qilingan sana
        """
        text = text.lower().strip()
        
        # 1. dateparser bilan urinib ko'rish
        try:
            parsed = date_parser.parse(
                text,
                languages=[lang.value],
                settings={'TIMEZONE': self.timezone.zone}
            )
            if parsed:
                return self.timezone.localize(parsed) if parsed.tzinfo is None else parsed
        except:
            pass
        
        # 2. Relative vaqtlarni qayta ishlash
        relative_result = self._parse_relative_time(text, lang)
        if relative_result:
            return relative_result
        
        # 3. Regex bilan qayta ishlash
        regex_result = self._parse_with_regex(text, lang)
        if regex_result:
            return regex_result
        
        return None
    
    def _parse_relative_time(self, text: str, lang: Language) -> Optional[datetime]:
        """Relative vaqtni tahlil qilish"""
        terms = self.relative_terms.get(lang, {})
        
        for term, value in terms.items():
            if term in text:
                if isinstance(value, int):
                    # Kunlar soni
                    result = self.now + timedelta(days=value)
                    result = self._apply_time_of_day(text, result, lang)
                    return result
                elif value == 'this_week':
                    # Haftaning oxirigacha
                    days_to_end = 6 - self.now.weekday()
                    result = self.now + timedelta(days=days_to_end)
                    return result.replace(hour=23, minute=59, second=59)
                elif value == 'next_week':
                    # Keyingi hafta
                    days_to_monday = 7 - self.now.weekday()
                    result = self.now + timedelta(days=days_to_monday)
                    return result.replace(hour=9, minute=0, second=0)
                elif value == 'weekend':
                    # Hafta oxiri
                    days_to_saturday = 5 - self.now.weekday()
                    if days_to_saturday < 0:
                        days_to_saturday += 7
                    result = self.now + timedelta(days=days_to_saturday)
                    return result.replace(hour=10, minute=0, second=0)
        
        return None
    
    def _apply_time_of_day(self, text: str, date: datetime, lang: Language) -> datetime:
        """Kun davomidagi vaqtni qo'shish"""
        time_of_day = {
            'morning': (9, 0),
            'afternoon': (14, 0),
            'evening': (18, 0),
            'night': (22, 0)
        }
        
        for term, (hour, minute) in time_of_day.items():
            if term in text:
                return date.replace(hour=hour, minute=minute, second=0)
        
        # Agar vaqt ko'rsatilmagan bo'lsa, default
        return date.replace(hour=12, minute=0, second=0)
    
    def _parse_with_regex(self, text: str, lang: Language) -> Optional[datetime]:
        """Regex bilan tahlil qilish"""
        patterns = [
            # 15:30, 3:30 PM
            r'(\d{1,2})[:.](\d{2})\s*(am|pm)?',
            # 15:30-16:00
            r'(\d{1,2})[:.](\d{2})\s*[-–]\s*(\d{1,2})[:.](\d{2})',
            # October 15 2025
            r'(\d{1,2})\s+(yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentabr|oktabr|noyabr|dekabr)\s+(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Soddalashtirilgan parse qilish
                    parsed = date_parser.parse(text, fuzzy=True)
                    if parsed:
                        return self.timezone.localize(parsed) if parsed.tzinfo is None else parsed
                except:
                    continue
        
        return None

class DurationNormalizer:
    """Davomiylikni normalizatsiya qilish"""
    
    def __init__(self):
        self.duration_patterns = {
            Language.UZBEK: {
                r'(\d+)\s+soat': 'hours',
                r'(\d+)\s+daqiqa': 'minutes',
                r'(\d+)\s+soat\s+(\d+)\s+daqiqa': 'hm',
                r'(\d+)\s+yarim\s+soat': 'minutes',  # 30 daqiqa
                r'butun\s+kun': 'allday'
            },
            Language.RUSSIAN: {
                r'(\d+)\s+час': 'hours',
                r'(\d+)\s+минут': 'minutes',
                r'(\d+)\s+час\s+(\d+)\s+минут': 'hm',
                r'(\d+)\s+полтора\s+час': 'minutes',  # 90 daqiqa
                r'весь\s+день': 'allday'
            },
            Language.ENGLISH: {
                r'(\d+)\s+hour': 'hours',
                r'(\d+)\s+minute': 'minutes',
                r'(\d+)\s+hour\s+(\d+)\s+minute': 'hm',
                r'(\d+)\s+and\s+a\s+half\s+hour': 'minutes',  # 90 daqiqa
                r'all\s+day': 'allday'
            }
        }
    
    def normalize(self, text: str, lang: Language) -> Optional[timedelta]:
        """
        Davomiylikni normalizatsiya qilish
        
        Args:
            text: Davomiylik matni
            lang: Til
            
        Returns:
            timedelta: Davomiylik
        """
        text = text.lower().strip()
        
        if text == 'allday' or 'all day' in text:
            return None  # Butun kun uchun alohida belgi
        
        patterns = self.duration_patterns.get(lang, {})
        
        for pattern, dtype in patterns.items():
            match = re.search(pattern, text)
            if match:
                if dtype == 'hours':
                    hours = int(match.group(1))
                    return timedelta(hours=hours)
                elif dtype == 'minutes':
                    minutes = int(match.group(1))
                    return timedelta(minutes=minutes)
                elif dtype == 'hm':
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    return timedelta(hours=hours, minutes=minutes)
        
        return None

class RepeatNormalizer:
    """Takrorlanishni normalizatsiya qilish"""
    
    def __init__(self):
        self.repeat_patterns = {
            Language.UZBEK: {
                'har kun': 'DAILY',
                'har hafta': 'WEEKLY',
                'har oy': 'MONTHLY',
                'har yil': 'YEARLY',
                'har dushanba': ('WEEKLY', 'MO'),
                'har seshanba': ('WEEKLY', 'TU'),
                'har chorshanba': ('WEEKLY', 'WE'),
                'har payshanba': ('WEEKLY', 'TH'),
                'har juma': ('WEEKLY', 'FR'),
                'har shanba': ('WEEKLY', 'SA'),
                'har yakshanba': ('WEEKLY', 'SU')
            },
            Language.RUSSIAN: {
                'каждый день': 'DAILY',
                'каждую неделю': 'WEEKLY',
                'каждый месяц': 'MONTHLY',
                'каждый год': 'YEARLY',
                'каждый понедельник': ('WEEKLY', 'MO'),
                'каждый вторник': ('WEEKLY', 'TU'),
                'каждую среду': ('WEEKLY', 'WE'),
                'каждый четверг': ('WEEKLY', 'TH'),
                'каждую пятницу': ('WEEKLY', 'FR'),
                'каждую субботу': ('WEEKLY', 'SA'),
                'каждое воскресенье': ('WEEKLY', 'SU')
            },
            Language.ENGLISH: {
                'every day': 'DAILY',
                'every week': 'WEEKLY',
                'every month': 'MONTHLY',
                'every year': 'YEARLY',
                'every monday': ('WEEKLY', 'MO'),
                'every tuesday': ('WEEKLY', 'TU'),
                'every wednesday': ('WEEKLY', 'WE'),
                'every thursday': ('WEEKLY', 'TH'),
                'every friday': ('WEEKLY', 'FR'),
                'every saturday': ('WEEKLY', 'SA'),
                'every sunday': ('WEEKLY', 'SU')
            }
        }
    
    def normalize(self, text: str, lang: Language, until_date: datetime = None) -> Optional[str]:
        """
        Takrorlanishni RRULE formatga o'tkazish
        
        Args:
            text: Takrorlanish matni
            lang: Til
            until_date: Tugash sanasi
            
        Returns:
            str: RRULE string
        """
        text = text.lower().strip()
        
        patterns = self.repeat_patterns.get(lang, {})
        
        for pattern, rule in patterns.items():
            if pattern in text:
                if isinstance(rule, tuple):
                    freq, day = rule
                    rrule_str = f"RRULE:FREQ={freq};BYDAY={day}"
                else:
                    rrule_str = f"RRULE:FREQ={rule}"
                
                if until_date:
                    rrule_str += f";UNTIL={until_date.strftime('%Y%m%dT%H%M%SZ')}"
                
                return rrule_str
        
        # "until" qismini ajratib olish
        until_match = re.search(r'until\s+([^,]+)', text, re.IGNORECASE)
        if until_match:
            # TODO: until sanasini parse qilish
            pass
        
        return None
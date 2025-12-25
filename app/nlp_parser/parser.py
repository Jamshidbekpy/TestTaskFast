import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time
from uuid import UUID

from .models import (
    ParseRequest, ParseResponse, ParsedEvent, Intent, Language, Slot
)
from.language_detector import LanguageDetector
from .normalizers import DateTimeNormalizer, DurationNormalizer, RepeatNormalizer
from .bert_model import BERTNLPModel
from .config import settings
from .exceptions import ParseError

class EventParser:
    """Asosiy event parser"""
    
    def __init__(self, model_dir: str = None):
        self.language_detector = LanguageDetector()
        self.bert_model = BERTNLPModel(model_dir)
        self.timezone = pytz.timezone(settings.default_timezone)
        
    def parse(self, request: ParseRequest) -> ParseResponse:
        """
        Promptni tahlil qilish
        
        Args:
            request: ParseRequest obyekti
            
        Returns:
            ParseResponse: Tahlil natijasi
        """
        start_time = time.time()
        
        try:
            prompt = request.prompt.strip()
            if not prompt:
                raise ParseError("Prompt cannot be empty")
            
            # 1. Tilni aniqlash
            if request.locale:
                language = request.locale
                lang_confidence = 1.0
            else:
                language, lang_confidence = self.language_detector.detect(prompt)
            
            # 2. Intentni aniqlash
            intent, intent_confidence = self.bert_model.predict_intent(prompt)
            
            # 3. Slotlarni ajratib olish
            raw_slots = self.bert_model.extract_slots(prompt)
            
            # 4. Slotlarni normalizatsiya qilish
            normalized_event = self._normalize_slots(
                prompt, raw_slots, language, request.user_timezone
            )
            
            # 5. Warninglarni tekshirish
            warnings = self._validate_event(normalized_event)
            
            # 6. ParsedEvent yaratish
            parsed_event = ParsedEvent(
                intent=intent,
                language=language,
                confidence=intent_confidence * lang_confidence,
                title=normalized_event.get('title'),
                all_day=normalized_event.get('all_day', False),
                time_start=normalized_event.get('time_start'),
                time_end=normalized_event.get('time_end'),
                repeat=normalized_event.get('repeat'),
                invites=normalized_event.get('invites', []),
                alerts=normalized_event.get('alerts', []),
                url=normalized_event.get('url'),
                note=normalized_event.get('note'),
                raw_slots=[Slot(**slot) for slot in raw_slots],
                normalized_text=self._reconstruct_text(prompt, raw_slots),
                warnings=warnings
            )
            
            processing_time = time.time() - start_time
            
            return ParseResponse(
                success=True,
                data=parsed_event,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ParseResponse(
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    def _normalize_slots(self, text: str, slots: List[Dict], 
                         language: Language, user_timezone: str) -> Dict:
        """Slotlarni normalizatsiya qilish"""
        result = {
            'title': None,
            'all_day': False,
            'time_start': None,
            'time_end': None,
            'repeat': None,
            'invites': [],
            'alerts': [],
            'url': None,
            'note': None
        }
        
        # Group slots by type
        slot_groups = {}
        for slot in slots:
            slot_type = slot['type']
            if slot_type not in slot_groups:
                slot_groups[slot_type] = []
            slot_groups[slot_type].append(slot['value'])
        
        # 1. Title
        if 'TITLE' in slot_groups:
            result['title'] = ' '.join(slot_groups['TITLE'])
        
        # 2. All day
        if 'ALLDAY' in slot_groups:
            result['all_day'] = True
        
        # 3. Datetime
        if 'DATETIME' in slot_groups:
            datetime_normalizer = DateTimeNormalizer(user_timezone)
            datetime_values = slot_groups['DATETIME']
            
            # Try to parse start and end times
            if len(datetime_values) >= 2:
                # Format: "10:00-11:00" yoki "10:00 dan 11:00 gacha"
                start_time = datetime_normalizer.normalize(datetime_values[0], language)
                end_time = datetime_normalizer.normalize(datetime_values[1], language)
                
                if start_time and end_time:
                    result['time_start'] = start_time
                    result['time_end'] = end_time
            elif len(datetime_values) == 1:
                # Single time, use default duration
                start_time = datetime_normalizer.normalize(datetime_values[0], language)
                if start_time:
                    result['time_start'] = start_time
                    result['time_end'] = start_time + timedelta(hours=settings.default_duration_hours)
        
        # 4. Duration
        if 'DURATION' in slot_groups and result['time_start'] and not result['time_end']:
            duration_normalizer = DurationNormalizer()
            duration_text = ' '.join(slot_groups['DURATION'])
            duration = duration_normalizer.normalize(duration_text, language)
            
            if duration and result['time_start']:
                result['time_end'] = result['time_start'] + duration
            elif 'allday' in duration_text.lower():
                result['all_day'] = True
                result['time_end'] = result['time_start'] + timedelta(days=1)
        
        # 5. Repeat
        if 'REPEAT' in slot_groups:
            repeat_normalizer = RepeatNormalizer()
            repeat_text = ' '.join(slot_groups['REPEAT'])
            result['repeat'] = repeat_normalizer.normalize(repeat_text, language)
        
        # 6. Alert
        if 'ALERT' in slot_groups:
            for alert_text in slot_groups['ALERT']:
                # Convert to ISO duration
                iso_duration = self._parse_alert(alert_text, language)
                if iso_duration:
                    result['alerts'].append(iso_duration)
        
        # 7. Invite
        if 'INVITE' in slot_groups:
            for invite in slot_groups['INVITE']:
                # Extract emails
                emails = re.findall(settings.email_pattern, invite)
                result['invites'].extend(emails)
        
        # 8. URL
        if 'URL' in slot_groups:
            url_text = ' '.join(slot_groups['URL'])
            urls = re.findall(settings.url_pattern, url_text)
            if urls:
                result['url'] = urls[0]
        
        # 9. NOTE
        if 'NOTE' in slot_groups:
            result['note'] = ' '.join(slot_groups['NOTE'])
        
        # 10. Extract title from text if not found
        if not result['title']:
            result['title'] = self._extract_title_from_text(text, slots)
        
        return result
    
    def _parse_alert(self, text: str, language: Language) -> Optional[str]:
        """Alertni ISO duration formatga o'tkazish"""
        text = text.lower()
        
        # Patterns for different languages
        patterns = {
            Language.UZBEK: [
                (r'(\d+)\s+daqiqa\s+oldin', 'minutes'),
                (r'(\d+)\s+soat\s+oldin', 'hours'),
                (r'(\d+)\s+kun\s+oldin', 'days')
            ],
            Language.RUSSIAN: [
                (r'(\d+)\s+минут\s+до', 'minutes'),
                (r'(\d+)\s+час\s+до', 'hours'),
                (r'(\d+)\s+день\s+до', 'days')
            ],
            Language.ENGLISH: [
                (r'(\d+)\s+minute', 'minutes'),
                (r'(\d+)\s+hour', 'hours'),
                (r'(\d+)\s+day', 'days')
            ]
        }
        
        lang_patterns = patterns.get(language, [])
        
        for pattern, unit in lang_patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                if unit == 'minutes':
                    return f"PT{value}M"
                elif unit == 'hours':
                    return f"PT{value}H"
                elif unit == 'days':
                    return f"P{value}D"
        
        return None
    
    def _extract_title_from_text(self, text: str, slots: List[Dict]) -> Optional[str]:
        """Matndan sarlavha ajratib olish"""
        # Remove known slot values
        cleaned_text = text
        for slot in slots:
            slot_value = slot['value']
            if slot['type'] != 'TITLE':
                cleaned_text = cleaned_text.replace(slot_value, '')
        
        # Extract text between quotes or after certain keywords
        quote_match = re.search(r'[\'"]([^\'"]+)[\'"]', text)
        if quote_match:
            return quote_match.group(1).strip()
        
        # Look for event-related keywords
        keywords = ['встреча', 'meeting', 'yig\'ilishi', 'событие', 'event', 'task']
        for keyword in keywords:
            if keyword in text.lower():
                # Extract text after keyword
                parts = text.lower().split(keyword)
                if len(parts) > 1:
                    possible_title = parts[1].strip().split('.')[0].split(',')[0]
                    if len(possible_title) > 3:
                        return possible_title.capitalize()
        
        return None
    
    def _reconstruct_text(self, original_text: str, slots: List[Dict]) -> str:
        """Normalizatsiya qilingan matnni qayta qurish"""
        # Simple reconstruction - in practice you might want more sophisticated
        reconstructed = original_text
        
        for slot in slots:
            if slot['type'] == 'DATETIME':
                # Replace datetime with normalized version
                pass
        
        return reconstructed
    
    def _validate_event(self, event: Dict) -> List[str]:
        """Event ma'lumotlarini tekshirish"""
        warnings = []
        
        # 1. Time validation
        if event.get('time_start') and event.get('time_end'):
            if event['time_start'] >= event['time_end']:
                warnings.append("Start time must be before end time")
        
        # 2. Duration validation
        if event.get('time_start') and event.get('time_end'):
            duration = event['time_end'] - event['time_start']
            if duration > timedelta(days=7):
                warnings.append("Event duration is too long (more than 7 days)")
        
        # 3. All-day event validation
        if event.get('all_day') and event.get('time_start'):
            if event['time_start'].hour != 0 or event['time_start'].minute != 0:
                warnings.append("All-day events should start at midnight")
        
        # 4. Alert validation
        for alert in event.get('alerts', []):
            if alert.startswith('P'):
                # Day-level alerts for non-all-day events
                if not event.get('all_day'):
                    warnings.append("Day-level alerts are recommended for all-day events only")
        
        return warnings
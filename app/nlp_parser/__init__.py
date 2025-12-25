"""
NLP Parser for Calendar Events
Multilingual (UZ/RU/EN) intent classification and slot filling using BERT-style models
"""

from .parser import EventParser
from .models import ParsedEvent, Intent, Slot
from .language_detector import LanguageDetector
from .normalizers import DateTimeNormalizer, RepeatNormalizer, DurationNormalizer
from .exceptions import ParseError, NormalizationError

__version__ = "1.0.0"
__all__ = [
    "EventParser",
    "ParsedEvent",
    "Intent",
    "Slot",
    "LanguageDetector",
    "DateTimeNormalizer",
    "RepeatNormalizer",
    "DurationNormalizer",
    "ParseError",
    "NormalizationError"
]
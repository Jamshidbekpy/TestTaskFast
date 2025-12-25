import os
from celery import Celery   
from ..core.settings import settings

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

from .beat_schedule import beat_schedule

celery_app.conf.beat_schedule = beat_schedule
celery_app.conf.timezone = 'Asia/Tashkent'
from app.worker.tasks import arithmetic # noqa
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .interfaces import AbstractEventRepository
from ...models import Event

class EventRepository(AbstractEventRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, **event_data):
        try:
            event = Event(**event_data)
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Event creation failed due to integrity error")
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error during event creation")

    def get_event_by_id(self, event_id):
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    def update_event(self, event_id, **event_data):
        event = self.get_event_by_id(event_id)
        for key, value in event_data.items():
            setattr(event, key, value)
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error during event update")

    def delete_event(self, event_id):
        event = self.get_event_by_id(event_id)
        try:
            self.db.delete(event)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error during event deletion")

    def list_events(self, filters=None):
        query = self.db.query(Event)
        if filters:
            for attr, value in filters.items():
                query = query.filter(getattr(Event, attr) == value)
        return query.all()
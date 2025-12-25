from fastapi import HTTPException, status

from .interfaces import AbstractEventService
from ...schemas.events_schemas import (
    EventCreateIn,
    EventCreateOut,
    EventUpdateIn,
    EventUpdateOut,
    EventRetrieveIn,
    EventRetrieveOut,
    EventDeleteIn,
    EventDeleteOut,
)
from ...repository.event.event_repo import EventRepository
from ...core.security import get_user_id_from_jwt

class EventService(AbstractEventService):

    def __init__(self, repo: EventRepository):
        self.repo = repo

    def create_event(self, event_in: EventCreateIn, access_token: str) -> EventCreateOut:
        
        user_id = get_user_id_from_jwt(access_token)
        event = self.repo.create_event(
            user_id=user_id,
            **event_in.model_dump()
        )
        return EventCreateOut.model_validate(event)

    def get_event(self, event_in: EventRetrieveIn, access_token: str) -> EventRetrieveOut:
        
        event = self.repo.get_event_by_id(event_in.id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        return EventRetrieveOut.model_validate(event)
    
    def update_event(
        self,
        event_id: str,
        event_in: EventUpdateIn,
        access_token: str
    ) -> EventUpdateOut:

        event = self.repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        updated_event = self.repo.update_event(
            event_id,
            **event_in.model_dump(exclude_unset=True)
        )

        return EventUpdateOut.model_validate(updated_event)

    def delete_event(self, event_in: EventDeleteIn, access_token: str) -> EventDeleteOut:
        event = self.repo.get_event_by_id(event_in.id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        self.repo.delete_event(event_in.id)

        return EventDeleteOut(
            message="Event successfully deleted"
        )

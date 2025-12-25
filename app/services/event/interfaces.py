from abc import ABC, abstractmethod
from ...schemas.events_schemas import (
    EventCreateIn, EventCreateOut, EventUpdateIn, EventUpdateOut, EventRetrieveIn, EventRetrieveOut, EventDeleteIn, EventDeleteOut
    )

class AbstractEventService(ABC):
    @abstractmethod
    def create_event(self, event_in: EventCreateIn) -> EventCreateOut:
        pass

    @abstractmethod
    def get_event(self, event_in: EventRetrieveIn) -> EventRetrieveOut:
        pass

    @abstractmethod
    def update_event(self, event_id: str, event_in: EventUpdateIn) -> EventUpdateOut:
        pass

    @abstractmethod
    def delete_event(self, event_in: EventDeleteIn) -> EventDeleteOut:
        pass
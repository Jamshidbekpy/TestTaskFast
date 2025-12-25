from abc import ABC, abstractmethod

class AbstractEventRepository(ABC):
    @abstractmethod
    def create_event(self, **event_data):
        pass

    @abstractmethod
    def get_event_by_id(self, event_id):
        pass

    @abstractmethod
    def update_event(self, event_id, **event_data):
        pass

    @abstractmethod
    def delete_event(self, event_id):
        pass

    @abstractmethod
    def list_events(self, filters=None):
        pass
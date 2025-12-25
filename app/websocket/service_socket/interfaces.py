from abc import ABC, abstractmethod
from fastapi import WebSocket


class AbstractWebSocketService(ABC):
    @abstractmethod
    async def handle_connection(self, websocket:WebSocket):
        pass
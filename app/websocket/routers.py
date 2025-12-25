from fastapi import APIRouter, WebSocket
from .manager import ConnectionManager
from .broker import RabbitMQBroker
from .service_socket.service import WebSocketService

router = APIRouter()
manager = ConnectionManager()
broker = RabbitMQBroker()
ws_service = WebSocketService(manager, broker)

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await ws_service.handle_connection(websocket)
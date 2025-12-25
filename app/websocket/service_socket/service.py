import json
from fastapi import WebSocket
from ..manager import ConnectionManager
from ..broker import RabbitMQBroker

class WebSocketService:
    def __init__(self, manager: ConnectionManager, broker: RabbitMQBroker):
        self.manager = manager
        self.broker = broker

    async def handle_connection(self, websocket: WebSocket):
        client_id = websocket.query_params.get("client_id")
        if not client_id:
            await websocket.close(code=1008)
            return

        await self.manager.connect(client_id, websocket)

        async def send_to_ws(message: str):
            await self.manager.send_to_client(client_id, message)

        await self.broker.connect(client_id, send_to_ws)

        try:
            while True:
                raw_message = await self.manager.receive_from(client_id)
                try:
                    data = json.loads(raw_message)
                    target = data["target"]
                    text = data["text"]
                except Exception as e:
                    print(f"[ERROR] JSON format xatolik: {e}")
                    continue

                await self.broker.publish(target, f"{client_id}: {text}")

        except Exception as e:
            print(f"[INFO] WebSocket uzildi: {e}")
            self.manager.disconnect(client_id)
            await self.broker.disconnect_consumer(client_id)

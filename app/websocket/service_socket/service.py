import json
from datetime import datetime
from jwt import decode
from fastapi import WebSocket
from ...core.settings import settings
from ..manager import ConnectionManager
from ..broker import RabbitMQBroker

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def get_user_id_from_jwt(token: str) -> int:
    payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload["sub"]


class WebSocketService:
    def __init__(self, manager: ConnectionManager, broker: RabbitMQBroker):
        self.manager = manager
        self.broker = broker

    async def handle_connection(self, websocket: WebSocket):
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008)
            return

        client_id = get_user_id_from_jwt(token)
        if not client_id:
            await websocket.close(code=1008)
            return

        client_id_str = str(client_id)
        await self.manager.connect(client_id_str, websocket)

        async def send_to_ws(processed_message: str):
            success = await self.manager.send_to_client(client_id_str, processed_message)
            if not success:
                print(f"[WARNING] Failed to send to client {client_id_str}")

        await self.broker.connect(client_id_str, send_to_ws)

        try:
            while True:
                raw_message = await websocket.receive_text()
                print(f"[INFO] Received from client {client_id_str}: {raw_message[:100]}")
                
                try:
                    data = json.loads(raw_message)
                    
                    # 1. Agar bu javob bo'lsa (response_to bor)
                    if "response_to" in data:
                        print(f"[DEBUG] Detected response: {data.get('response_to')}")
                        await self.broker.process_response(client_id_str, raw_message)
                        continue
                    
                    # 2. Oddiy xabar bo'lsa
                    text = data.get("text", raw_message)
                    enhanced_data = {
                        "text": text,
                        "timestamp": datetime.now().isoformat(),
                        "client_id": client_id_str
                    }
                    message_to_send = json.dumps(enhanced_data)
                    
                except json.JSONDecodeError:
                    # Oddiy text bo'lsa
                    message_to_send = json.dumps({
                        "text": raw_message,
                        "timestamp": datetime.now().isoformat(),
                        "client_id": client_id_str
                    })

                # Xabarni brokerga yuborish
                await self.broker.publish(client_id_str, message_to_send)
                print(f"[INFO] Sent to broker for processing: {message_to_send[:100]}")

        except Exception as e:
            print(f"[ERROR] WebSocket error for {client_id_str}: {e}")
            self.manager.disconnect(client_id_str)
            await self.broker.disconnect_consumer(client_id_str)
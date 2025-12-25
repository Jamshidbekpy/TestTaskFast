from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.connections = {}
        
        
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[client_id] = websocket
        print(f"[INFO] Client {client_id} connected")
        
        
    def disconnect(self, client_id: str):
        if client_id in self.connections:
            del self.connections[client_id]
            print(f"[INFO] Client {client_id} disconnected")
        
    
    async def send_to_client(self, client_id: str, message: str):
        websocket = self.connections.get(client_id)
        
        if not websocket:
            print(f"[WARNING] Client {client_id} not found in active connections")
            return False
            
        try:
            await websocket.send_text(message)
            print(f"[INFO] Message sent to client {client_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message to client {client_id}: {e}")
            # Connection muammo bo'lsa, disconnect qilish
            self.disconnect(client_id)
            return False
        
    async def receive_from(self, client_id: str):
        websocket = self.connections.get(client_id)
        
        if not websocket:
            print(f"[WARNING] Client {client_id} not found for receiving")
            return None
            
        try:
            return await websocket.receive_text()
        except Exception as e:
            print(f"[ERROR] Failed to receive from client {client_id}: {e}")
            return None
    
    def get_connection_count(self) -> int:
        return len(self.connections)
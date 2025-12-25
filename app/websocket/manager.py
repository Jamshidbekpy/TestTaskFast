from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections = {}
        
        
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[client_id] = websocket
        
        
    def disconnect(self, client_id:str):
        self.connections.pop(client_id, None)
        
    
    async def send_to_client(self, client_id:str, message:str):
        try:
            websocket = self.connections.get(client_id)
        except:
            return f"Ushbu {client_id} li connection mavjud emas!"
            
        else:
            try:
                await websocket.send_text(message)
            except:
                print("Xabar yuborishda xatolik!")
        
    async def receive_from(self, client_id:str):
        try:
            websocket = self.connections.get(client_id)
        except:
            print(f"Xabarni olish uchun ushbu{client_id} li shaxs topilmadi")
        else:
            return await websocket.receive_text()
            
         
        
        
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.users: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        
        if user_id not in self.users:
            self.users[user_id] = []

        self.users[user_id].append(websocket) 

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id not in self.users:
            return

        # O(N) to remove but unlikely to be large
        # May also leave empty list which uses up memory
        self.users[user_id].remove(websocket)

    async def send(self, user_id: int, data: str):
        if user_id not in self.users:
            return
        
        for connection in self.users[user_id]:
            await connection.send_text(data)

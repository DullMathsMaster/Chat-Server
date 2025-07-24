from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager
import time
import json

class BasicDB:
    """
    Basic DB implementation. Not thread-safe.
    """
    def __init__(self):
        self.dms: dict[tuple[int, int], list[tuple[str, int]]] = {}

    def get_dm_key(self, sender: int, receiver: int) -> tuple[int, int]:
        return tuple(sorted([sender, receiver]))
    
    async def insert_dm(self, sender: int, receiver: int, content: str, timestamp: int) -> int:
        key = self.get_dm_key(sender, receiver)
        
        if key not in self.dms:
            self.dms[key] = []
        
        self.dms[key].append((content, timestamp))

        return len(self.dms[key]) - 1

class RequestHandler:
    def __init__(self, manager: ConnectionManager, db: BasicDB):
        self.manager = manager
        self.db = db

    async def send_direct(self, user_id: int, request: dict):
        dest = int(request.get("dest"))
        content = request.get("content")
        timestamp = int(time.time_ns() / 1_000_000)

        message_id = await self.db.insert_dm(user_id, dest, content, timestamp)

        data = {
            "type": "recv[direct]",
            "sender": user_id, 
            "content": content, 
            "timestamp": timestamp, 
            "id": message_id
        }

        print(data)

        await manager.send(dest, json.dumps(data))

    async def handle(self, user_id: int, request: dict):
        action = request.get("type")
        
        if action == "send[direct]":
            await self.send_direct(user_id, request)

app = FastAPI()
manager = ConnectionManager()
db = BasicDB()
handler = RequestHandler(manager, db)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)

    try:
        while True:
            # Can error if JSON invalid.
            # Assume fully valid for now.

            request = await websocket.receive_json()
            print(user_id, request)

            await handler.handle(user_id, request)

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

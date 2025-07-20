from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# https://fastapi.tiangolo.com/advanced/websockets/#handling-disconnections-and-multiple-clients

class Manager:
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

    async def send(self, user_id: int, data: dict):
        if user_id not in self.users:
            return
        
        for connection in self.users[user_id]:
            await connection.send_json(data)

manager = Manager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)

    try:
        await manager.send(user_id, f"#{user_id} joined the chat")

        while True:
            # Can error if JSON invalid.
            data = await websocket.receive_json()
            print(user_id, data)

            for user in data["users"]:
                await manager.send(user, data)
        
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

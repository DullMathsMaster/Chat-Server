from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from . import models, database, dependencies
from datetime import datetime

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)




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
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(dependencies.get_db)):
    await manager.connect(user_id, websocket)

    try:
        await manager.send(user_id, f"#{user_id} joined the chat")

        while True:
            # Can error if JSON invalid.
            data = await websocket.receive_json()
            print(user_id, data)
            
            now_time = str(datetime.now())
            message = models.Message(recipient = data["users"][1],
                            sender = data["users"][0],
                            time = now_time,
                            read = False,
                            content = data["text"])
                                     
            db.add(message)
            db.commit()
            data["time"] = now_time
            
            for user in data["users"]:
                await manager.send(user, data)
        
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)


@app.websocket("/messagesws/{user_id}")
async def reload(websocket: WebSocket, user_id: int, db: Session = Depends(dependencies.get_db)):
    await manager.connect(user_id, websocket)
    print("hi")
    try:
        await manager.send(user_id, f"#{user_id} joined the chat")
        print("bye")
        while True:
            print("wilson")
            data = await websocket.receive_json()
            print(data)
            other=data["users"][1]
            print(data)
            messages = db.query(models.Message).filter(
                (models.Message.sender == user_id) |
                (models.Message.recipient == other)
            ).all()


            message_list = [
                {
                    "id": m.message_id,
                    "sender": m.sender,
                    "recipient": m.recipient,
                    "time": 4,
                    "read": m.read,
                    "content": m.content
                }
                for m in messages
            ]


            await websocket.send_json({
                "type": "message_history",
                "messages": message_list
            })

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
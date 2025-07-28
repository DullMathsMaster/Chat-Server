from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime

from chat_server.manager import Manager
from chat_server.db.basic_db import BasicDB
from chat_server.handler import RequestHandler


app = FastAPI()
manager = Manager()
db = BasicDB()
handler = RequestHandler(manager, db)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()

    manager.add(user_id, websocket)
    
    try:
        while True:
            # Can error if JSON invalid.
            # Assume fully valid for now.

            request = await websocket.receive_json()
            print(user_id, request)
            
            await handler.handle(user_id, request)

    except WebSocketDisconnect:
        manager.remove(user_id, websocket)

@app.websocket("/messagesws/{user_id}")
async def message_ws_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()

    manager.add(user_id, websocket)
    
    try:
        while True:
            # Can error if JSON invalid.
            # Assume fully valid for now.

            request = await websocket.receive_json()
            print(user_id, request)
            
            await handler.handle(user_id, request)

    except WebSocketDisconnect:
        manager.remove(user_id, websocket)
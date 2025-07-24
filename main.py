from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from chat_server.manager.ws_manager import WSManager
from chat_server.db.basic_db import BasicDB
from chat_server.handler.request_handler import RequestHandler

app = FastAPI()
manager = WSManager()
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

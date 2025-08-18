from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from chat_server import Manager, DB, RequestHandler


app = FastAPI()
manager = Manager()
db = DB("sqlite+pysqlite:///database.db")
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

            await handler.handle(user_id, request)

    except WebSocketDisconnect:
        manager.remove(user_id, websocket)

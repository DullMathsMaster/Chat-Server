from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from chat_server import DB, Manager, RequestHandler, types


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
            
            try:
                request = await websocket.receive_json()  # print(user_id, request)
                base = types.Action(**request)
                model_cls = types.action_models.get(base.type)

                if not model_cls:
                    print("unkown type")
                    continue

                # compare to type
                data = model_cls(**request)

                await handler.handle(user_id, data)


            except ValidationError as e:
                print(e)


    except WebSocketDisconnect:
        manager.remove(user_id, websocket)

import time
import json

from chat_server.db import DB
from chat_server.manager import Manager

from . import Handler

__all__ = ["RequestHandler"]

class RequestHandler(Handler):
    def __init__(self, manager: Manager, db: DB):
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

        await self.manager.send(dest, json.dumps(data))

    async def handle(self, user_id: int, request: dict):
        action = request.get("type")
        
        if action == "send[direct]":
            await self.send_direct(user_id, request)

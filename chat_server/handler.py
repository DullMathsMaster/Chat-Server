import time
from json import dumps
from asyncio import gather

from chat_server.db import DB
from chat_server.manager import Manager

__all__ = ["RequestHandler"]

class RequestHandler:
    def __init__(self, manager: Manager, db: DB):
        self.manager = manager
        self.db = db

    async def send_direct(self, user_id: int, request: dict):
        recipient = int(request.get("recipient"))
        content = request.get("content")
        timestamp = int(time.time_ns() / 1_000_000)

        message_id = await self.db.insert_dm(user_id, recipient, content, timestamp)

        data = dumps({
            "type": "recv[direct]",
            "sender": user_id,
            "recipient": recipient,
            "content": content, 
            "timestamp": timestamp, 
            "id": message_id
        })

        tasks = [self.manager.send(i, data) for i in [user_id, recipient]]
        await gather(*tasks)

    async def handle(self, user_id: int, request: dict):
        """
        Handles the request for the user.
        """
        action = request.get("type")
        
        if action == "send[direct]":
            await self.send_direct(user_id, request)

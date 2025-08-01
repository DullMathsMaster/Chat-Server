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
        recipient = request.get("recipient")
        content = request.get("content")

        timestamp = int(time.time_ns() / 1_000_000)

        message_id = await self.db.insert_dm(user_id, recipient, content, timestamp)

        data = dumps(
            {
                "type": "recv[direct]",
                "sender": user_id,
                "recipient": recipient,
                "content": content,
                "timestamp": timestamp,
                "id": message_id,
            }
        )

        # Use a set to only send once if sending to self
        tasks = [self.manager.send(i, data) for i in {user_id, recipient}]
        await gather(*tasks)

    async def get_user(self, user_id: int, request: dict):
        target_user = request.get("user")

        user = await self.db.find_user(target_user)

        data = dumps(...)

        await self.manager.send(user_id, data)

    async def set_user(self, user_id: int, request: dict):
        name = request.get("name")
        desc = request.get("desc")

        user = await self.db.create_user(user_id, name, desc)

        data = dumps(...)

        await self.manager.send(user_id, data)

    async def get_direct(self, user_id: int, request: dict):
        recipient = request.get("recipient")
        message_id = request.get("id")

        message = await self.db.get_message(user_id, recipient, message_id)

        data = dumps(...)

        await self.manager.send(user_id, data)

    async def reload_messages(self, user_id: int, request: dict):
        recipient = request.get("recipient")
        timestamp = request.get("timestamp")

        messages = await self.db.return_conversation(user_id, recipient, timestamp)

        data = dumps(...)

        tasks = [self.manager.send(user_id, d) for d in data]
        await gather(*tasks)

    async def handle(self, user_id: int, request: dict):
        """
        Handles the request for the user.
        """
        action = request.get("type")

        if action == "send[direct]":
            await self.send_direct(user_id, request)

        elif action == "get[direct]":
            await self.get_direct(user_id, request)

        elif action == "get[user]":
            await self.get_user(user_id, request)

        elif action == "set[user]":
            await self.set_user(user_id, request)

        elif action == "update":
            await self.reload_messages(user_id, request)

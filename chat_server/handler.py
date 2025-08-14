import time
from asyncio import gather
from json import dumps

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

        sequence_no = await self.db.insert_dm(user_id, recipient, content, timestamp)

        data = dumps(
            {
                "type": "recv[direct]",
                "sender": user_id,
                "recipient": recipient,
                "content": content,
                "timestamp": timestamp,
                "seq_no": sequence_no,
            }
        )

        # Use a set to only send once if sending to self
        tasks = [self.manager.send(i, data) for i in {user_id, recipient}]
        await gather(*tasks)

    async def get_user(self, user_id: int, request: dict):
        match = request.get("user_id")
        user = await self.db.find_user(match)
        
        if not user:
            print(f"user {user_id} not found")
            return

        data = dumps(
            {
                "type": "recv[user]",
                "user_id": user.user_id,
                "image": user.image,
                "name": user.name,
                "desc": user.desc,
            }
        )

        await self.manager.send(user_id, data)

    async def set_user(self, user_id: int, request: dict):
        name = request.get("name")
        desc = request.get("desc")

        user = await self.db.create_user(user_id, name, desc)

        data = dumps(
            {
                "type": "recv[user]",
                "user_id": user.user_id,
                "image": user.image,
                "name": user.name,
                "desc": user.desc,
            }
        )

        await self.manager.send(user_id, data)

    async def get_direct(self, user_id: int, request: dict):
        recipient = request.get("recipient")
        sequence_no = request.get("seq_no")

        message = await self.db.get_message(user_id, recipient, sequence_no)

        data = dumps(
            {
                "type": "recv[direct]",
                "sender": message.sender,
                "recipient": message.recipient,
                "content": message.content,
                "timestamp": message.timestamp,
                "seq_no": message.sequence_no,
            }
        )

        await self.manager.send(user_id, data)

    async def reload_messages(self, user_id: int, request: dict):
        recipient = request.get("recipient")
        timestamp = request.get("timestamp")

        messages = await self.db.return_conversation(user_id, recipient, timestamp)

        data = [
            dumps(
                {
                    "type": "recv[direct]",
                    "sender": msg.sender,
                    "recipient": msg.recipient,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "seq_no": msg.sequence_no,
                }
            )
            for msg in messages
        ]

        tasks = [self.manager.send(user_id, d) for d in data]
        await gather(*tasks)

    async def handle(self, user_id: int, request: dict):
        """
        Handles the request for the user.
        """
        request_type = request.get("type")

        actions = {
            "send[direct]": self.send_direct,
            "get[direct]": self.get_direct,
            "get[user]": self.get_user,
            "set[user]": self.set_user,
            "update": self.reload_messages,
        }

        action = actions.get(request_type)

        if action is None:
            return

        await action(user_id, request)

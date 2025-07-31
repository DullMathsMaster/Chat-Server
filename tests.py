from unittest import IsolatedAsyncioTestCase, main
from json import loads

from chat_server.db import DB
from chat_server.handler import RequestHandler


class DummyManager:
    def __init__(self):
        self.log = []

    async def send(self, user_id: int, data: str):
        self.log.append((user_id, loads(data)))


db = DB("sqlite+pysqlite:///data/tests.db")


class HandlerTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.manager = DummyManager()
        self.handler = RequestHandler(self.manager, db)

    async def test_send_direct(self):
        await self.handler.send_direct(
            1, {"type": "send[direct]", "recipient": 2, "content": "hello"}
        )

        users = {1, 2}

        for recipient, data in self.manager.log:
            # Ensure content is as expected
            self.assertEqual(data["sender"], 1)
            self.assertEqual(data["recipient"], 2)
            self.assertEqual(data["content"], "hello")

            users.remove(recipient)

        # Ensure every user in DM receives message
        self.assertEqual(len(users), 0)


if __name__ == "__main__":
    main()

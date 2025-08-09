from unittest import IsolatedAsyncioTestCase, main
from json import loads

from chat_server.db import DB
from chat_server.handler import RequestHandler


class DummyManager:
    def __init__(self):
        self.log: list[tuple[int, dict]] = []

    async def send(self, user_id: int, data: str):
        self.log.append((user_id, loads(data)))


class HandlerTest(IsolatedAsyncioTestCase):
    def setUp(self):
        db = DB("sqlite+pysqlite:///:memory:")
        self.manager = DummyManager()
        self.handler = RequestHandler(self.manager, db)

    async def test_send_direct(self):
        await self.handler.send_direct(
            1, {"type": "send[direct]", "recipient": 2, "content": "hello"}
        )

        users = set()
        expected = {
            "type": "recv[direct]",
            "sender": 1,
            "recipient": 2,
            "content": "hello",
            "seq_no": 0,
        }

        for recipient, data in self.manager.log:
            # Check data has above fields to be correct
            self.assertLessEqual(expected.items(), data.items())
            users.add(recipient)

        # Ensure every user in DM receives message
        self.assertEqual(users, {1, 2})

    async def test_send_direct_self(self):
        await self.handler.send_direct(
            1, {"type": "send[direct]", "recipient": 1, "content": "hello"}
        )

        users = set()
        expected = {
            "type": "recv[direct]",
            "sender": 1,
            "recipient": 1,
            "content": "hello",
            "seq_no": 0,
        }

        # Ideally only send once but multiple times is also fine

        for recipient, data in self.manager.log:
            self.assertLessEqual(expected.items(), data.items())
            users.add(recipient)

        self.assertEqual(users, {1})

    async def test_get_direct(self):
        await self.handler.send_direct(
            1, {"type": "send[direct]", "recipient": 2, "content": "hi, 2"}
        )

        await self.handler.send_direct(
            2, {"type": "send[direct]", "recipient": 1, "content": "hi, 1"}
        )

        self.manager.log.clear()

        await self.handler.get_direct(
            1, {"type": "get[direct]", "recipient": 2, "seq_no": 0}
        )

        expected = {
            "type": "recv[direct]",
            "sender": 1,
            "recipient": 2,
            "content": "hi, 2",
            "seq_no": 0,
        }

        for recipient, data in self.manager.log:
            self.assertLessEqual(expected.items(), data.items())
            self.assertEqual(recipient, 1)


if __name__ == "__main__":
    main()

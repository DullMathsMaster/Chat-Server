from json import loads
from unittest import IsolatedAsyncioTestCase, main

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

    def tearDown(self):
        self.handler.db.close()

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


    # actions = {
    #         "send[direct]": self.send_direct,
    #         "get[direct]": self.get_direct,
    #         "get[user]": self.get_user,
    #         "set[user]": self.set_user,
    #         "update": self.reload_messages,
    #     }
    
    async def test_create_user(self):
        await self.handler.set_user(
            1, {"type": "set[user]", "name": "Alice", "desc": "A user"}
        )

        expected = {
            "type": "recv[user]",
            "user_id": 1,
            "image": None,
            "name": "Alice",
            "desc": "A user",
        }

        for recipient, data in self.manager.log:
            self.assertLessEqual(expected.items(), data.items())
            self.assertEqual(recipient, 1)

    async def test_get_user(self):
        await self.handler.set_user(
            1, {"type": "set[user]", "name": "Alice", "desc": "A user"}
        )

        self.manager.log.clear()

        await self.handler.get_user(1, {"type": "get[user]", "user_id": 1})

        expected = {
            "type": "recv[user]",
            "user_id": 1,
            "image": None,
            "name": "Alice",
            "desc": "A user",
        }

        for recipient, data in self.manager.log:
            self.assertLessEqual(expected.items(), data.items())
            self.assertEqual(recipient, 1)

    async def test_reload_messages(self):
        messages = [
            "hello",
            "how are you?",
            "goodbye"
        ]

        for message in messages:
            await self.handler.send_direct(
                1, {"type": "send[direct]", "recipient": 2, "content": message}
            )
            

        

        self.manager.log.clear()

        await self.handler.reload_messages(
            1, {"type": "reload", "recipient": 2, "timestamp": 1}
        )

        expected_messages = [
            {
            "type": "recv[direct]",
            "sender": 1,
            "recipient": 2,
            "content": "hello",
            "seq_no": 0,
            },
            {
            "type": "recv[direct]",
            "sender": 1,
            "recipient": 2,
            "content": "how are you?",
            "seq_no": 1,
            },
            {
            "type": "recv[direct]",
            "sender": 1,
            "recipient": 2,
            "content": "goodbye",
            "seq_no": 2,
            },
        ]

        for i, expected in enumerate(expected_messages):
            recipient, data = self.manager.log[i]
            self.assertLessEqual(expected.items(), data.items())
            self.assertEqual(recipient, 1)
    
    async def test_unknown_action(self):
        await self.handler.handle(1, {"type": "unknown[action]"})
        print("bladjasdfhjasgfhj")
        # No log entries should be made for unknown actions
        self.assertEqual(self.manager.log, [])


if __name__ == "__main__":
    main()

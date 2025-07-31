from unittest import IsolatedAsyncioTestCase

from chat_server.manager import Manager
from chat_server.db import DB
from chat_server.handler import RequestHandler

manager = Manager()
db = DB("sqlite+pysqlite:///data/tests.db")
handler = RequestHandler(manager, db)


class Test(IsolatedAsyncioTestCase): ...

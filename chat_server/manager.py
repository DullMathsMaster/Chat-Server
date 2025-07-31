from asyncio import gather

from fastapi import WebSocket

__all__ = ["Manager"]


class Manager:
    def __init__(self) -> None:
        self.users: dict[int, list[WebSocket]] = {}

    def add(self, user_id: int, websocket: WebSocket) -> None:
        """
        Adds the websocket connection to the user.
        """

        if user_id not in self.users:
            self.users[user_id] = []

        self.users[user_id].append(websocket)

    def remove(self, user_id: int, websocket: WebSocket) -> None:
        """
        Removes the websocket connection from the user.
        """
        if user_id not in self.users:
            return

        # O(N) to remove but unlikely to be large
        # May also leave empty list which uses up memory
        self.users[user_id].remove(websocket)

    async def send(self, user_id: int, data: str) -> None:
        """
        Send data to all websockets for that user.
        """
        if user_id not in self.users:
            return

        tasks = [socket.send_text(data) for socket in self.users[user_id]]
        await gather(*tasks)

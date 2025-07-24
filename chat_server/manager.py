from fastapi import WebSocket

__all__ = ["Manager"]

class Manager:
    def __init__(self):
        self.users: dict[int, list[WebSocket]] = {}

    async def add(self, user_id: int, websocket: WebSocket):
        """
        Adds the websocket connection to the user.
        """
        await websocket.accept()
        
        if user_id not in self.users:
            self.users[user_id] = []

        self.users[user_id].append(websocket) 

    def remove(self, user_id: int, websocket: WebSocket):
        """
        Removes the websocket connection from the user.
        """
        if user_id not in self.users:
            return

        # O(N) to remove but unlikely to be large
        # May also leave empty list which uses up memory
        self.users[user_id].remove(websocket)

    async def send(self, user_id: int, data: str):
        """
        Send data to all websockets for that user.
        """
        if user_id not in self.users:
            return
        
        for connection in self.users[user_id]:
            await connection.send_text(data)

from abc import ABC, abstractmethod

from fastapi import WebSocket

__all__ = ["Manager"]

class Manager(ABC):
    @abstractmethod
    async def connect(self, user_id: int, websocket: WebSocket):
        ...

    @abstractmethod
    def disconnect(self, user_id: int, websocket: WebSocket):
        ...

    @abstractmethod
    async def send(self, user_id: int, data: str):
        ...
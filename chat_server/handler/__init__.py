from abc import ABC, abstractmethod

__all__ = ["Handler"]

class Handler(ABC):
    @abstractmethod
    async def handle(self, user_id: int, request: dict):
        ...

from abc import ABC, abstractmethod

__all__ = ["DB"]

class DB(ABC):
    @abstractmethod
    async def insert_dm(self, sender: int, recipient: int, content: str, timestamp: int) -> int:
        """
        Saves a direct message into the DB and returns its corresponding ID.
        """
        ...

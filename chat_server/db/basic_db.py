from . import DB, SessionLocal, Message

__all__ = ["BasicDB"]

class BasicDB(DB):
    """
    Basic DB implementation. Not thread-safe.
    """
    def __init__(self):
        self.dms: dict[tuple[int, int], list[tuple[str, int]]] = {}

    def get_dm_key(self, sender: int, recipient: int) -> tuple[int, int]:
        return tuple(sorted([sender, recipient]))
    
    def return_conversation(self, sender: int, recipient: int, limit: int = 100) -> list[tuple[int, int, str, int]]:
        """
        Returns conversation between two users as a list of tuples.
        Each tuple contains: (sender, recipient, content, timestamp)
        """
        db = SessionLocal() 
        messages = db.query(Message).filter(
            (
                (Message.sender == sender) & (Message.recipient == recipient) |
                (Message.sender == recipient) & (Message.recipient == sender)
            )
        ).order_by(Message.timestamp.asc()).limit(limit).all()
        
        message_list = [
            (msg.sender, msg.recipient, msg.content, msg.timestamp)
            for msg in messages
        ]
        db.close()
        return message_list



# class BasicDB(DB):
#     """
#     Basic DB implementation. Not thread-safe.
#     """
#     def __init__(self):
#         self.dms: dict[tuple[int, int], list[tuple[str, int]]] = {}

#     def get_dm_key(self, sender: int, receiver: int) -> tuple[int, int]:
#         return tuple(sorted([sender, receiver]))
    
#     async def insert_dm(self, sender: int, recipient: int, content: str, timestamp: int) -> int:
#         key = self.get_dm_key(sender, recipient)
        
#         if key not in self.dms:
#             self.dms[key] = []
        
#         self.dms[key].append((content, timestamp))

#         return len(self.dms[key]) - 1

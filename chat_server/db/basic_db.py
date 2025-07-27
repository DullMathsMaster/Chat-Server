from . import DB

__all__ = ["BasicDB"]

class BasicDB(DB):
    """
    Basic DB implementation. Not thread-safe.
    """
    def __init__(self):
        self.dms: dict[tuple[int, int], list[tuple[str, int]]] = {}

    def get_dm_key(self, sender: int, receiver: int) -> tuple[int, int]:
        return tuple(sorted([sender, receiver]))
    



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

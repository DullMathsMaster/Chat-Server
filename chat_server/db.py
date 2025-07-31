from sqlalchemy.orm import Session
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

__all__ = ["DB", "SessionLocal", "Message"]

DATABASE_URL = "sqlite+pysqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    image = Column(String)
    name = Column(String, nullable=False)
    desc = Column(String)


class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    recipient = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)


class DB:
    async def insert_dm(
        self, sender: int, recipient: int, content: str, timestamp: int
    ) -> int:
        """
        Saves a direct message into the DB and returns its corresponding ID.
        """

        db = SessionLocal()

        message = Message(
            recipient=recipient,
            sender=sender,
            timestamp=timestamp,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)
        db.close()

        return message.message_id

    async def return_conversation(
        self, sender: int, recipient: int, timestamp: int, limit: int = 100
    ) -> list[tuple[int, int, str, int]]:
        """
        Returns conversation between two users as a list of tuples.
        Each tuple contains: (sender, recipient, content, timestamp)
        """
        db = SessionLocal()
        messages = (
            db.query(Message)
            .filter(
                (
                    ((Message.sender == sender) & (Message.recipient == recipient)
                    | (Message.sender == recipient) & (Message.recipient == sender))
                    & (Message.timesstamp >= timestamp)
                )
            )
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .all()
        )

        message_list = [
            {
                "sender": msg.sender,
                "recipient": msg.recipient,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "id": msg.message_id
            }
            for msg in messages
        ]
        db.close()
        return message_list

    async def find_user(self, user_id: int) -> tuple[int, str, str, str]:
        db = SessionLocal()
        user = db.query(Users).filter(Users.user_id == user_id).first() #.first returns none if not there
        db.close()
        return user
    
    async def create_user(self, user_id: int, name: str, desc: str) -> str:
        db = SessionLocal()

        user = Users(user_id = user_id,
                           image = "",
                           name = name,
                           desc = desc
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return "success"
    
    async def get_message(self, sender: int, recipient: int, message_id: id) -> dict:
        db = SessionLocal()
        message = (
            db.query(Message)
            .filter(
                (
                    ((Message.sender == sender) & (Message.recipient == recipient)
                    | (Message.sender == recipient) & (Message.recipient == sender))
                    & (Message.message_id == message_id)

                )
            )
        )

        message = {"sender": message[0].sender, 
                   "recipient": message[0].recipient, 
                   "content": message[0].content, 
                   "timesstamp": message[0].timestamp,
                   "id": message[0].message_id}
        db.close()
        return message

    

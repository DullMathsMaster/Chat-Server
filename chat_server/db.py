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


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(Integer, primary_key=True, nullable=False)
    image = Column(String)
    name = Column(String, nullable=False)
    bio = Column(String)


class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    message_type = Column(String, default="DM")
    sender = Column(Integer, ForeignKey("user_profiles.user_id"), nullable=False)
    recipient = Column(Integer, ForeignKey("user_profiles.user_id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    read = Column(Boolean, nullable=False, default=False)


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
            read=False,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)
        db.close()

        return message.message_id

    def return_conversation(
        self, sender: int, recipient: int, limit: int = 100
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
                    (Message.sender == sender) & (Message.recipient == recipient)
                    | (Message.sender == recipient) & (Message.recipient == sender)
                )
            )
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .all()
        )

        message_list = [
            (msg.sender, msg.recipient, msg.content, msg.timestamp) for msg in messages
        ]
        db.close()
        return message_list

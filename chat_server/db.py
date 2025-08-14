import uuid
from typing import Optional

from sqlalchemy import ColumnElement, ForeignKey, and_, create_engine, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

__all__ = ["DB"]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[Optional[str]]
    name: Mapped[str]
    desc: Mapped[Optional[str]]


class Message(Base):
    __tablename__ = "message"

    message_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sequence_no: Mapped[int]
    sender: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    recipient: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    content: Mapped[str]
    timestamp: Mapped[int]


def has_chat(user1: int, user2: int) -> ColumnElement[bool]:
    return or_(
        and_(Message.sender == user1, Message.recipient == user2),
        and_(Message.sender == user2, Message.recipient == user1),
    )


class DB:
    def __init__(self, url: str):
        self.engine = create_engine(url, connect_args={"check_same_thread": False})
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def close(self):
        self.engine.dispose()

    async def insert_dm(
        self, sender: int, recipient: int, content: str, timestamp: int
    ) -> int:
        """
        Saves a direct message into the DB and returns its corresponding sequence number.
        """

        with self.Session() as db:
            row = (
                db.query(Message.sequence_no)
                .filter(has_chat(sender, recipient))
                .order_by(Message.timestamp.desc())
                .first()
            )

            seq_no = row._tuple()[0] + 1 if row else 0

            message = Message(
                sequence_no=seq_no,
                recipient=recipient,
                sender=sender,
                timestamp=timestamp,
                content=content,
            )

            db.add(message)
            db.commit()
            db.refresh(message)

        return message.sequence_no

    async def return_conversation(
        self, sender: int, recipient: int, timestamp: int, limit: int = 100
    ) -> list[Message]:
        """
        Returns conversation between two users as a list of tuples.
        Each tuple contains: (sender, recipient, content, timestamp)
        """
        db = self.Session()

        messages = (
            db.query(Message)
            .filter(has_chat(sender, recipient), Message.timestamp >= timestamp)
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .all()
        )

        db.close()
        return messages

    async def find_user(self, user_id: int) -> User | None:
        db = self.Session()

        user = db.query(User).filter(User.user_id == user_id).first()

        db.close()
        return user

    async def create_user(self, user_id: int, name: str, desc: str) -> User:
        db = self.Session()

        user = User(user_id=user_id, name=name, desc=desc)

        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user

    async def get_message(
        self, sender: int, recipient: int, sequence_no: int
    ) -> Message | None:
        db = self.Session()

        message = (
            db.query(Message)
            .filter(has_chat(sender, recipient), Message.sequence_no == sequence_no)
            .first()
        )

        db.close()
        return message

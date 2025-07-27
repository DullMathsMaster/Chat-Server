
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from abc import ABC, abstractmethod
from fastapi import Depends

__all__ = ["DB"]

DATABASE_URL = "sqlite+pysqlite:///././database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_uuid():
    return str(uuid.uuid4())

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(String(36), primary_key=True, default=generate_uuid, nullable=False)
    image = Column(String)
    name = Column(String, nullable=False)
    bio = Column(String)

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    message_type = Column(String, nullable=False)
    sender = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    recipient = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    read = Column(Boolean, nullable=False, default=False)

Base.metadata.create_all(bind=engine)



class DB(ABC):
    @abstractmethod
    async def insert_dm(self, sender: int, recipient: int, content: str, timestamp: int, db: Session = Depends(get_db)) -> int:
        """
        Saves a direct message into the DB and returns its corresponding ID.
        """
        message_id = generate_uuid()
        message = Message( message_id = message_id,
                        recipient = recipient,
                        sender = sender,
                        timestamp = timestamp,
                        read = False,
                        content = content)
                                    
        db.add(message)
        db.commit()
        return message_id

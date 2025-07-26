from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String(36), primary_key=True, default=generate_uuid, nullable=False)
    image = Column(String)  # Can also be Text
    name = Column(String, nullable=False)
    bio = Column(String)

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    recipient = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    sender = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    time = Column(String(), nullable=False,)
    read = Column(Boolean, nullable=False, default=False)
    content = Column(String, nullable=False)

import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


def _utcnow():
    """Timezone-aware UTC timestamp (replaces deprecated datetime.utcnow)."""
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at.asc()"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    conversation = relationship("Conversation", back_populates="messages")

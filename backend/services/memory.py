import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Conversation, Message
from config import settings

logger = logging.getLogger("rag_pipeline")

class Memory:
    def __init__(self, max_turns: int = None, max_assistant_chars: int = None):
        self.max_turns = max_turns if max_turns is not None else settings.max_history_turns
        self.message_limit = self.max_turns * 2
        self.max_assistant_chars = (
            max_assistant_chars if max_assistant_chars is not None else settings.max_assistant_chars
        )

    def get_history(self, session_id: str) -> str:

        with SessionLocal() as db:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()

            if not conversation:
                return ""

            recent_messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.desc())
                .limit(self.message_limit)
                .all()
            )
            recent_messages.reverse()

            if not recent_messages:
                return ""

            # structured turn summaries
            history_parts = []
            for msg in recent_messages:
                role = msg.role
                content = msg.content.strip()
                if role == "assistant":
                    if len(content) > self.max_assistant_chars:
                        content = content[:self.max_assistant_chars].rstrip() + "..."
                    history_parts.append(f"<assistant_summary>{content}</assistant_summary>")
                else:
                    history_parts.append(f"<user>{content}</user>")

            return "\n".join(history_parts)

    @staticmethod
    def condense_history_xml(history_xml: str) -> str:
        """Convert pre-fetched XML history to a condensed plain-text format 
        which avoids duplicate db queries.
        """
        if not history_xml:
            return ""

        lines = []
        for line in history_xml.split("\n"):
            if line.startswith("<user>") and line.endswith("</user>"):
                lines.append(f"User: {line[6:-7]}")
            elif line.startswith("<assistant_summary>") and line.endswith("</assistant_summary>"):
                lines.append(f"Assistant: {line[19:-20]}")
        return "\n".join(lines)

    def get_condensed_history(self, session_id: str) -> str:
        """fetches history from DB and condenses it.
        """
        return self.condense_history_xml(self.get_history(session_id))

    def add_message(self, session_id: str, user_message: str, assistant_message: str):

        with SessionLocal() as db:

            try:
                conversation = db.query(Conversation).filter(
                    Conversation.session_id == session_id
                ).first()
    
                if not conversation:
                    conversation = Conversation(session_id=session_id)
                    db.add(conversation)
                    db.flush()
    
                user_msg = Message(conversation_id=conversation.id, role="user", content=user_message)
                assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=assistant_message)
                db.add_all([user_msg, assistant_msg])
                db.commit()

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to save messages for session={session_id}: {e}", exc_info=True)
                raise

    def clear_history(self, session_id: str) -> bool:
        """Delete all messages for a session."""

        with SessionLocal() as db:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()

            if conversation:
                db.delete(conversation)
                db.commit()
                return True
            return False

    def list_sessions(self):

        with SessionLocal() as db:
            conversations = db.query(Conversation).order_by(
                Conversation.updated_at.desc()
            ).all()

            return [
                {
                    "session_id": conv.session_id,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                }
                for conv in conversations
            ]
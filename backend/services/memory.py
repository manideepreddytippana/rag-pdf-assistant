from sqlalchemy.orm import Session
from database import SessionLocal
from models import Conversation, Message

class Memory:
    def __init__(self, max_turns: int = 5):
        self.message_limit = max_turns * 2

    def get_history(self, session_id: str):

        with SessionLocal() as db:
            conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()

            if conversation:
                recent_messages = conversation.messages[-self.message_limit:]

                history = []
                for message in recent_messages:
                    role = "User" if message.role == "user" else "Assistant"
                    history.append(f"{role}: {message.content}")
                return "\n".join(history)
            return ""

    def add_message(self, session_id: str, user_message: str, assistant_message: str):

        with SessionLocal() as db:

            try:
                conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
                if not conversation:
                    conversation = Conversation(session_id=session_id)
                    db.add(conversation)
                    db.flush()
    
                user_msg = Message(conversation_id=conversation.id, role="user", content=user_message)
                assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=assistant_message)
                db.add_all([user_msg, assistant_msg])
                db.commit()

            except Exception:
                db.rollback()
                raise Exception("Failed to interact with PostgreSQL DB")

                
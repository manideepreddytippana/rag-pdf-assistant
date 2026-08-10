from pydantic import BaseModel, Field
from typing import List, Optional

class UserRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    session_id: str = "session_id"

class SourceInfo(BaseModel):
    source: str
    page_no: int
    score: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    question: str
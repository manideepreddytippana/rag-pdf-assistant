from pydantic import BaseModel, Field
from typing import List

class UserRequest(BaseModel):
    prompt: str = Field( min_length = 1,max_length = 4000)
    session_id: str = "session_id"

class ModelResponse(BaseModel):
    response: str
    
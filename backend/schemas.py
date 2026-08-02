from pydantic import BaseModel, Field
from typing import List

class UserRequest(BaseModel):
    prompt: str = Field( min_length = 1,max_length = 4000)

class ModelResponse(BaseModel):
    response: str
    
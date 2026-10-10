
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    session_id: str
    video_id: str
    question: str
    history: list[ChatMessage] = Field(default_factory=list)

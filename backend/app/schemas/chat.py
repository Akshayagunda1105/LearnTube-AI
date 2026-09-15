from pydantic import BaseModel


class ChatRequest(BaseModel):
    video_id: str
    question: str
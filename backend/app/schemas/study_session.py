from pydantic import BaseModel, Field


class CreateStudySessionRequest(BaseModel):
    video_id: str = Field(min_length=1)
    video_url: str = Field(min_length=1)
    title: str = ""
    thumbnail: str = ""
    original_language: str = ""
    original_language_code: str = ""
    original_transcript: list = []
    english_transcript: list = []
from pydantic import BaseModel, Field


class VideoProcessRequest(BaseModel):
    video_id: str = Field(min_length=1)
    video_url: str = Field(min_length=1)
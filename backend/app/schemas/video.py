from pydantic import BaseModel


class VideoProcessRequest(BaseModel):
    video_id: str
from fastapi import APIRouter, HTTPException
from app.services.youtube_service import extract_video_id
from app.services.transcript_service import fetch_transcript


router = APIRouter(
    prefix="/api/videos",
    tags=["Videos"]
)


@router.post("/transcript")
def get_transcript(url: str):
    try:
        video_id = extract_video_id(url)

        transcript = fetch_transcript(video_id)

        return {
            "video_id": video_id,
            "transcript": transcript
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch transcript: {str(error)}"
        )
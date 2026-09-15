from fastapi import APIRouter, HTTPException

from app.schemas.video import VideoProcessRequest
from app.services.youtube_service import extract_video_id
from app.services.transcript_service import fetch_transcript
from app.services.rag_pipeline_service import get_video_rag


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


@router.post("/process")
def process_video(request: VideoProcessRequest):
    try:
        rag_data = get_video_rag(request.video_id)

        return {
            "video_id": rag_data["video_id"],
            "language": rag_data["language"],
            "language_code": rag_data["language_code"],
            "is_generated": rag_data["is_generated"],
            "chunk_count": len(rag_data["rag_chunks"]),
            "message": "Video processed successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(error)}"
        )
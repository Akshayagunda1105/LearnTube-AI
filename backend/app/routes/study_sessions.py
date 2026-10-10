from fastapi import APIRouter, Depends, HTTPException
from app.services.quiz_service import generate_quiz
from app.middleware.auth import get_current_user_id
from app.schemas.study_session import CreateStudySessionRequest
from app.services.study_session_service import (
    create_study_session,
    get_study_session,
    get_user_study_sessions,
    update_study_session_summary,
    update_study_session_notes,
    update_study_session_quiz,
)
from app.services.summarizer_service import (
    create_summary_chunks,
    summarize_chunk,
    combine_chunk_summaries,
    generate_final_summary,
)
from app.services.notes_service import (
    create_note_chunks,
    generate_chunk_notes,
    combine_note_sections,
)


router = APIRouter(
    prefix="/api/study-sessions",
    tags=["Study Sessions"]
)


@router.post("")
def create_session(
    request: CreateStudySessionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a study session for the authenticated user.
    """

    try:
        return create_study_session(
            user_id=user_id,
            video_id=request.video_id,
            video_url=request.video_url,
            title=request.title,
            thumbnail=request.thumbnail,
            original_language=request.original_language,
            original_language_code=request.original_language_code,
            original_transcript=request.original_transcript,
            english_transcript=request.english_transcript,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("")
def get_sessions(
    user_id: str = Depends(get_current_user_id),
):
    """
    Retrieve all study sessions belonging to the authenticated user.
    """

    try:
        return get_user_study_sessions(user_id)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/{session_id}")
def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Retrieve one study session belonging to the authenticated user.
    """

    try:
        session = get_study_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        return session

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/{session_id}/summary")
def generate_session_summary(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Generate and store an AI summary for a study session.
    """

    try:
        session = get_study_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        english_transcript = session["english_transcript"]

        if not english_transcript:
            raise HTTPException(
                status_code=400,
                detail="English transcript is not available"
            )

        summary_chunks = create_summary_chunks(
            english_transcript
        )

        chunk_summaries = []

        for chunk in summary_chunks:
            chunk_summary = summarize_chunk(chunk)
            chunk_summaries.append(chunk_summary)

        combined_summaries = combine_chunk_summaries(
            chunk_summaries
        )

        final_summary = generate_final_summary(
            combined_summaries
        )

        updated_session = update_study_session_summary(
            session_id=session_id,
            user_id=user_id,
            summary=final_summary,
        )

        if updated_session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        return {
            "session_id": session_id,
            "summary": final_summary,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(error)}"
        )


@router.post("/{session_id}/notes")
def generate_session_notes(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Generate and store AI notes for a study session.
    """

    try:
        # 1. Retrieve the study session.
        session = get_study_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        # 2. Get the English transcript.
        english_transcript = session["english_transcript"]

        if not english_transcript:
            raise HTTPException(
                status_code=400,
                detail="English transcript is not available"
            )

        # 3. Split the transcript into manageable chunks.
        note_chunks = create_note_chunks(
            english_transcript
        )

        # 4. Generate notes for each chunk.
        note_sections = []

        for chunk in note_chunks:
            note_section = generate_chunk_notes(chunk)
            note_sections.append(note_section)

        # 5. Combine all generated sections.
        final_notes = combine_note_sections(
            note_sections
        )

        # 6. Store the notes in MongoDB.
        updated_session = update_study_session_notes(
            session_id=session_id,
            user_id=user_id,
            notes=final_notes,
        )

        if updated_session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found"
            )

        # 7. Return the generated notes.
        return {
            "session_id": session_id,
            "notes": final_notes,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate notes: {str(error)}"
        )


@router.post("/{session_id}/quiz")
def generate_session_quiz(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Generate and save an MCQ quiz for a study session.
    """

    try:
        # 1. Retrieve the session and verify ownership.
        session = get_study_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found",
            )

        # 2. Use the English transcript for question generation.
        english_transcript = session["english_transcript"]

        if not english_transcript:
            raise HTTPException(
                status_code=400,
                detail="English transcript is not available",
            )

        # 3. Generate and validate the quiz.
        quiz_data = generate_quiz(english_transcript)
        questions = quiz_data["questions"]

        # 4. Save the quiz to MongoDB.
        updated_session = update_study_session_quiz(
            session_id=session_id,
            user_id=user_id,
            quiz=questions,
        )

        if updated_session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found",
            )

        # 5. Do not expose answers before quiz submission.
        safe_questions = [
            {
                "question": question["question"],
                "options": question["options"],
            }
            for question in questions
        ]

        return {
            "session_id": session_id,
            "questions": safe_questions,
            "message": "Quiz generated successfully",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quiz: {str(error)}",
        )


@router.post("/{session_id}/quiz/submit")
def submit_session_quiz(
    session_id: str,
    answers: dict,
    user_id: str = Depends(get_current_user_id),
):
    """
    Grade submitted quiz answers on the backend.
    """

    try:
        session = get_study_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Study session not found",
            )

        questions = session.get("quiz", [])

        if not questions:
            raise HTTPException(
                status_code=400,
                detail="Generate a quiz before submitting answers",
            )

        submitted_answers = answers.get("answers")

        if not isinstance(submitted_answers, dict):
            raise HTTPException(
                status_code=400,
                detail="Answers must be provided as a dictionary",
            )

        if len(submitted_answers) != len(questions):
            raise HTTPException(
                status_code=400,
                detail="Please answer every question before submitting",
            )

        results = []
        score = 0

        for index, question in enumerate(questions):
            question_id = str(index)

            if question_id not in submitted_answers:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing answer for question {index + 1}",
                )

            selected_answer = submitted_answers[question_id]
            options = question["options"]
            correct_answer = question["correct_answer"]

            if selected_answer not in options:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid option for question {index + 1}",
                )

            is_correct = selected_answer == correct_answer

            if is_correct:
                score += 1

            results.append({
                "question": question["question"],
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question["explanation"],
            })

        return {
            "session_id": session_id,
            "score": score,
            "total_questions": len(questions),
            "percentage": round(score / len(questions) * 100, 2),
            "results": results,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to grade quiz: {str(error)}",
        )

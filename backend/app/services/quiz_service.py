
import logging
from typing import Annotated

from dotenv import load_dotenv
from google import genai
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

load_dotenv()

logger = logging.getLogger(__name__)

client = genai.Client()

MODEL_NAME = "gemini-2.5-flash"
MAX_OUTPUT_ATTEMPTS = 2

NonEmptyString = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]

def make_gemini_schema(model):
    """Build a JSON schema without unsupported additionalProperties fields."""
    schema = model.model_json_schema()

    def clean_schema(value):
        if isinstance(value, dict):
            value.pop("additionalProperties", None)
            for child in value.values():
                clean_schema(child)
        elif isinstance(value, list):
            for child in value:
                clean_schema(child)

    clean_schema(schema)
    return schema


class QuizQuestion(BaseModel):
    """Validated structure for one multiple-choice question."""

    model_config = ConfigDict(extra="forbid")

    question: NonEmptyString
    options: list[NonEmptyString] = Field(
        min_length=4,
        max_length=4,
    )
    correct_answer: NonEmptyString
    explanation: NonEmptyString

    @field_validator("options")
    @classmethod
    def validate_distinct_options(cls, options):
        normalized_options = [
            option.casefold() for option in options
        ]

        if len(set(normalized_options)) != 4:
            raise ValueError(
                "Each question must have four distinct options"
            )

        return options

    @model_validator(mode="after")
    def validate_correct_answer(self):
        if self.correct_answer not in self.options:
            raise ValueError(
                "The correct answer must match one of the options"
            )

        return self


class QuizResponse(BaseModel):
    """Validated structure for the complete quiz."""

    model_config = ConfigDict(extra="forbid")

    questions: list[QuizQuestion] = Field(
        min_length=10,
        max_length=10,
    )


def generate_quiz(english_transcript):
    """
    Generate exactly 10 multiple-choice questions.

    Each question contains:
    - question
    - options (exactly four distinct options)
    - correct_answer
    - explanation
    """

    if (
        not isinstance(english_transcript, list)
        or not english_transcript
    ):
        raise ValueError("English transcript cannot be empty")

    transcript_parts = []

    for segment in english_transcript:
        if not isinstance(segment, dict):
            raise ValueError(
                "Transcript segments must be dictionaries"
            )

        text = segment.get("text", "")

        if isinstance(text, str) and text.strip():
            transcript_parts.append(text.strip())

    transcript_text = "\n".join(transcript_parts)

    if not transcript_text.strip():
        raise ValueError(
            "English transcript contains no usable text"
        )

    # Keep the prompt within a reasonable size for longer videos.
    transcript_text = transcript_text[:30000]

    prompt = f"""
You are creating a quiz for a student learning from an educational video.

Generate exactly 10 multiple-choice questions based only on the transcript.

Rules:
- Use only information explicitly supported by the transcript.
- Do not invent facts or use outside knowledge.
- Test understanding, not just memorization.
- Include exactly four distinct options for each question.
- There must be exactly one correct option.
- The correct_answer must exactly match one option.
- Make incorrect options plausible but clearly incorrect based on the transcript.
- Keep questions and explanations clear and concise.
- Avoid duplicate questions.
- Return only valid JSON without Markdown fences.

Required JSON structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Option A",
      "explanation": "Explanation supported by the transcript"
    }}
  ]
}}

Transcript:
{transcript_text}
"""

    last_error = None

    for attempt in range(MAX_OUTPUT_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": make_gemini_schema(QuizResponse),
                },
            )

            response_text = (response.text or "").strip()

            if not response_text:
                raise ValueError(
                    "Gemini returned an empty quiz response"
                )

            quiz = QuizResponse.model_validate_json(
                response_text
            )

            return quiz.model_dump()

        except (ValidationError, ValueError) as error:
            last_error = error

            logger.warning(
                "Quiz output validation failed on attempt %s/%s: %s",
                attempt + 1,
                MAX_OUTPUT_ATTEMPTS,
                error,
            )

            if attempt < MAX_OUTPUT_ATTEMPTS - 1:
                prompt += """

Your previous response did not satisfy the required JSON schema.
Generate the entire quiz again. Ensure exactly 10 questions,
exactly four distinct options per question, and a correct answer
that exactly matches one of the options. Return valid JSON only.
"""

    logger.error(
        "Quiz generation failed after %s attempts",
        MAX_OUTPUT_ATTEMPTS,
    )

    raise ValueError(
        "Could not generate a valid quiz. Please try again."
    ) from last_error

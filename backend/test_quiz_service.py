
import json

import pytest
from pydantic import ValidationError

from app.services.quiz_service import (
    QuizQuestion,
    QuizResponse,
    generate_quiz,
)


def make_valid_quiz():
    """Create a valid quiz containing exactly 10 questions."""
    questions = []

    for index in range(10):
        questions.append({
            "question": f"Question {index + 1}?",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ],
            "correct_answer": "Option A",
            "explanation": "Supported by the provided transcript.",
        })

    return {"questions": questions}


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeModels:
    def __init__(self, responses):
        self.responses = responses
        self.calls = 0

    def generate_content(self, **kwargs):
        response = self.responses[self.calls]
        self.calls += 1
        return FakeResponse(response)


class FakeClient:
    def __init__(self, responses):
        self.models = FakeModels(responses)


def install_fake_client(monkeypatch, responses):
    fake_client = FakeClient(responses)

    monkeypatch.setattr(
        "app.services.quiz_service.client",
        fake_client,
    )

    return fake_client


def test_valid_quiz_is_accepted():
    quiz = QuizResponse.model_validate(make_valid_quiz())

    assert len(quiz.questions) == 10
    assert len(quiz.questions[0].options) == 4
    assert quiz.questions[0].correct_answer == "Option A"


def test_quiz_with_nine_questions_is_rejected():
    quiz = make_valid_quiz()
    quiz["questions"].pop()

    with pytest.raises(ValidationError):
        QuizResponse.model_validate(quiz)


def test_question_with_three_options_is_rejected():
    question = {
        "question": "What is binary search?",
        "options": ["Option A", "Option B", "Option C"],
        "correct_answer": "Option A",
        "explanation": "A sample explanation.",
    }

    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(question)


def test_duplicate_options_are_rejected():
    question = {
        "question": "What is binary search?",
        "options": [
            "Sorted array",
            "sorted array",
            "Option C",
            "Option D",
        ],
        "correct_answer": "Sorted array",
        "explanation": "A sample explanation.",
    }

    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(question)


def test_correct_answer_not_in_options_is_rejected():
    question = {
        "question": "What is binary search?",
        "options": [
            "Option A",
            "Option B",
            "Option C",
            "Option D",
        ],
        "correct_answer": "Option E",
        "explanation": "A sample explanation.",
    }

    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(question)


def test_empty_question_text_is_rejected():
    question = {
        "question": "   ",
        "options": [
            "Option A",
            "Option B",
            "Option C",
            "Option D",
        ],
        "correct_answer": "Option A",
        "explanation": "A sample explanation.",
    }

    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(question)


def test_malformed_gemini_json_is_retried(monkeypatch):
    valid_json = json.dumps(make_valid_quiz())

    fake_client = install_fake_client(
        monkeypatch,
        [
            '{"questions": [',
            valid_json,
        ],
    )

    result = generate_quiz([
        {"text": "Binary search works on sorted arrays."}
    ])

    assert len(result["questions"]) == 10
    assert fake_client.models.calls == 2


def test_invalid_output_after_retry_raises_error(monkeypatch):
    fake_client = install_fake_client(
        monkeypatch,
        [
            '{"questions": [',
            '{"questions": [',
        ],
    )

    with pytest.raises(
        ValueError,
        match="Could not generate a valid quiz",
    ):
        generate_quiz([
            {"text": "Binary search works on sorted arrays."}
        ])

    assert fake_client.models.calls == 2


def test_empty_transcript_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        generate_quiz([])


def test_transcript_without_usable_text_is_rejected():
    with pytest.raises(
        ValueError,
        match="no usable text",
    ):
        generate_quiz([
            {"text": "   "},
            {"text": None},
        ])


def test_gemini_schema_excludes_additional_properties():
    from app.services.quiz_service import (
        QuizResponse,
        make_gemini_schema,
    )

    schema = make_gemini_schema(QuizResponse)

    def check_schema(value):
        if isinstance(value, dict):
            assert "additionalProperties" not in value
            for child in value.values():
                check_schema(child)
        elif isinstance(value, list):
            for child in value:
                check_schema(child)

    check_schema(schema)

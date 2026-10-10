
import { useEffect, useState } from "react";
import api from "../services/api";

function QuizPanel({ sessionId, savedQuiz = [] }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let cancelled = false;

    async function restoreQuiz() {
      setQuestions([]);
      setAnswers({});
      setResults(null);
      setError("");

      if (savedQuiz.length === 0) {
        return;
      }

      // Restore the saved questions.
      const safeQuestions = savedQuiz.map((question) => ({
        question: question.question,
        options: question.options,
      }));

      setQuestions(safeQuestions);

      try {
        const response = await api.get(
          `/api/study-sessions/${sessionId}`
        );

        if (cancelled) return;

        const attempts = response.data.quiz_attempts || [];

        if (attempts.length > 0) {
          // Restore the most recent completed attempt.
          const latestAttempt = attempts[attempts.length - 1];

          setResults({
            session_id: sessionId,
            ...latestAttempt,
          });

          // Restore selected answers for display.
          const restoredAnswers = {};

          latestAttempt.results?.forEach((result, index) => {
            if (result.selected_answer) {
              restoredAnswers[String(index)] =
                result.selected_answer;
            }
          });

          setAnswers(restoredAnswers);
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Could not restore quiz results:", err);
          setError("Could not load previous quiz results.");
        }
      }
    }

    restoreQuiz();

    return () => {
      cancelled = true;
    };
  }, [sessionId, savedQuiz]);
  const handleGenerateQuiz = async () => {
    setLoading(true);
    setError("");
    setQuestions([]);
    setAnswers({});
    setResults(null);

    try {
      const response = await api.post(
        `/api/study-sessions/${sessionId}/quiz`
      );

      setQuestions(response.data.questions);
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Could not generate the quiz. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAnswer = (questionIndex, option) => {
    if (results) return;

    setAnswers((previous) => ({
      ...previous,
      [String(questionIndex)]: option,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (Object.keys(answers).length !== questions.length) {
      setError("Please answer every question before submitting.");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const response = await api.post(
        `/api/study-sessions/${sessionId}/quiz/submit`,
        { answers }
      );

      setResults(response.data);
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Could not submit your quiz. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="quiz-panel">
      <div className="quiz-panel__header">
        <div>
          <p className="eyebrow">CHECK YOUR UNDERSTANDING</p>
          <h2>Test what you've learned.</h2>
          <p>
            Practice with questions generated from this video's
            English transcript.
          </p>
        </div>

        <button
          type="button"
          className="button button--primary"
          onClick={handleGenerateQuiz}
          disabled={loading || submitting}
        >
          {loading
            ? "Generating quiz..."
            : questions.length > 0
              ? "Generate new quiz"
              : savedQuiz.length > 0
                ? "Start quiz"
                : "Generate quiz"}
        </button>
      </div>

      {loading && (
        <p className="page-feedback">
          Creating questions from your video. This may take a moment...
        </p>
      )}

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}

      {questions.length > 0 && (
        <div className="quiz-panel__questions">
          {questions.map((question, index) => {
            const result = results?.results?.[index];

            return (
              <article
                className="quiz-question"
                key={`${index}-${question.question}`}
              >
                <p className="quiz-question__number">
                  QUESTION {index + 1} OF {questions.length}
                </p>

                <h3>{question.question}</h3>

                <div className="quiz-question__options">
                  {question.options.map((option, optionIndex) => {
                    const isSelected =
                      answers[String(index)] === option;

                    const isCorrect =
                      results && option === result?.correct_answer;

                    const isWrongSelection =
                      results &&
                      isSelected &&
                      !result?.is_correct;

                    let optionClass = "quiz-option";

                    if (isSelected) {
                      optionClass += " quiz-option--selected";
                    }

                    if (isCorrect) {
                      optionClass += " quiz-option--correct";
                    }

                    if (isWrongSelection) {
                      optionClass += " quiz-option--incorrect";
                    }

                    return (
                      <button
                        type="button"
                        key={optionIndex}
                        className={optionClass}
                        onClick={() =>
                          handleSelectAnswer(index, option)
                        }
                        disabled={Boolean(results) || submitting}
                      >
                        <span className="quiz-option__letter">
                          {String.fromCharCode(65 + optionIndex)}
                        </span>
                        <span>{option}</span>
                      </button>
                    );
                  })}
                </div>

                {results && (
                  <div className="quiz-question__feedback">
                    <p>
                      <strong>
                        {result.is_correct
                          ? "Correct"
                          : "Not quite"}
                      </strong>
                    </p>

                    {!result.is_correct && (
                      <p>
                        Correct answer: {result.correct_answer}
                      </p>
                    )}

                    <p>{result.explanation}</p>
                  </div>
                )}
              </article>
            );
          })}

          {!results ? (
            <button
              type="button"
              className="button button--primary"
              onClick={handleSubmitQuiz}
              disabled={submitting || loading}
            >
              {submitting ? "Checking answers..." : "Submit answers"}
            </button>
          ) : (
            <div className="quiz-result">
              <p className="eyebrow">YOUR RESULT</p>
              <h3>
                {results.score} / {results.total_questions}
              </h3>
              <p>{results.percentage}% score</p>

              <button
                type="button"
                className="button button--secondary"
                onClick={handleGenerateQuiz}
                disabled={loading}
              >
                Try another quiz
              </button>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export default QuizPanel;


import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

function StudySession() {
  const { sessionId } = useParams();

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState("");

  useEffect(() => {
    const loadSession = async () => {
      try {
        const response = await api.get(
          `/api/study-sessions/${sessionId}`
        );

        setSession(response.data);
      } catch (err) {
        console.error(err);

        const detail = err.response?.data?.detail;

        if (typeof detail === "string") {
          setError(detail);
        } else {
          setError("Could not load this study session.");
        }
      } finally {
        setLoading(false);
      }
    };

    loadSession();
  }, [sessionId]);

  const handleGenerateSummary = async () => {
    setSummaryLoading(true);
    setSummaryError("");

    try {
      const response = await api.post(
        `/api/study-sessions/${sessionId}/summary`
      );

      const generatedSummary = response.data.summary;

      setSession((previousSession) => ({
        ...previousSession,
        summary: generatedSummary,
      }));
    } catch (err) {
      console.error(err);

      const detail = err.response?.data?.detail;

      if (typeof detail === "string") {
        setSummaryError(detail);
      } else {
        setSummaryError("Could not generate the summary. Please try again.");
      }
    } finally {
      setSummaryLoading(false);
    }
  };

  if (loading) {
    return (
      <div>
        <h1>Study Session</h1>
        <p>Loading study session...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1>Study Session</h1>
        <p>{error}</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div>
        <h1>Study Session</h1>
        <p>Study session not found.</p>
      </div>
    );
  }

  const summary = session.summary;

  return (
    <div>
      <h1>Study Session</h1>

      <h2>Video</h2>

      <p>
        <strong>Video ID:</strong> {session.video_id}
      </p>

      <p>
        <strong>Video URL:</strong>{" "}
        <a
          href={session.video_url}
          target="_blank"
          rel="noreferrer"
        >
          Open YouTube Video
        </a>
      </p>

      <h2>Transcript Information</h2>

      <p>
        <strong>Original Language:</strong>{" "}
        {session.original_language || "Unknown"}
      </p>

      <p>
        <strong>Language Code:</strong>{" "}
        {session.original_language_code || "Unknown"}
      </p>

      <p>
        <strong>Original Transcript Segments:</strong>{" "}
        {session.original_transcript?.length || 0}
      </p>

      <p>
        <strong>English Transcript Segments:</strong>{" "}
        {session.english_transcript?.length || 0}
      </p>

      <h2>AI Summary</h2>

      {!summary && (
        <div>
          <p>Generate an AI-powered summary of this video.</p>

          <button
            type="button"
            onClick={handleGenerateSummary}
            disabled={summaryLoading}
          >
            {summaryLoading
              ? "Generating Summary..."
              : "Generate AI Summary"}
          </button>
        </div>
      )}

      {summaryError && <p role="alert">{summaryError}</p>}

      {summaryLoading && (
        <p>Please wait while the AI prepares your summary.</p>
      )}

      {summary && (
        <div>
          <h3>Overview</h3>
          <p>{summary.overview}</p>

          <h3>Key Points</h3>

          {summary.key_points?.length > 0 ? (
            <ul>
              {summary.key_points.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
          ) : (
            <p>No key points available.</p>
          )}

          <h3>Key Concepts</h3>

          {summary.concepts?.length > 0 ? (
            <div>
              {summary.concepts.map((concept, index) => (
                <div key={index}>
                  <h4>{concept.title}</h4>
                  <p>{concept.explanation}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>No concepts available.</p>
          )}

          <h3>Takeaways</h3>

          {summary.takeaways?.length > 0 ? (
            <ul>
              {summary.takeaways.map((takeaway, index) => (
                <li key={index}>{takeaway}</li>
              ))}
            </ul>
          ) : (
            <p>No takeaways available.</p>
          )}
        </div>
      )}

      <h2>AI Notes</h2>

      <p>
        <strong>Notes:</strong>{" "}
        {session.notes?.length
          ? "Available"
          : "Not generated yet"}
      </p>
    </div>
  );
}

export default StudySession;

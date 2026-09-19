import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

function StudySession() {
  const { sessionId } = useParams();

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

      <h2>AI Content</h2>

      <p>
        <strong>Summary:</strong>{" "}
        {session.summary ? "Available" : "Not generated yet"}
      </p>

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
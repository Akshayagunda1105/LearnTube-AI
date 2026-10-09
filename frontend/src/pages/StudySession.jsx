
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import TranscriptViewer from "../components/TranscriptViewer";
import ChatPanel from "../components/ChatPanel";

function StudySession() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState("");
  const [notesLoading, setNotesLoading] = useState(false);
  const [notesError, setNotesError] = useState("");

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError("");

      try {
        const [sessionResponse, historyResponse] =
          await Promise.all([
            api.get(`/api/study-sessions/${sessionId}`),
            api.get("/api/study-sessions"),
          ]);

        setSession(sessionResponse.data);
        setSessions(historyResponse.data);
      } catch (err) {
        console.error(err);
        const detail = err.response?.data?.detail;

        setError(
          typeof detail === "string"
            ? detail
            : "Could not load this study session."
        );
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [sessionId]);

  const handleGenerateSummary = async () => {
    setSummaryLoading(true);
    setSummaryError("");

    try {
      const response = await api.post(
        `/api/study-sessions/${sessionId}/summary`
      );

      setSession((previous) => ({
        ...previous,
        summary: response.data.summary,
      }));
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;

      setSummaryError(
        typeof detail === "string"
          ? detail
          : "Could not generate the summary. Please try again."
      );
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleGenerateNotes = async () => {
    setNotesLoading(true);
    setNotesError("");

    try {
      const response = await api.post(
        `/api/study-sessions/${sessionId}/notes`
      );

      setSession((previous) => ({
        ...previous,
        notes: response.data.notes,
      }));
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;

      setNotesError(
        typeof detail === "string"
          ? detail
          : "Could not generate notes. Please try again."
      );
    } finally {
      setNotesLoading(false);
    }
  };

  const formatDate = (value) => {
    if (!value) return "Date unavailable";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "Date unavailable";
    }

    return date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  if (loading) {
    return (
      <main className="study-page-feedback">
        <p>Preparing your study space...</p>
      </main>
    );
  }

  if (error || !session) {
    return (
      <main className="study-page-feedback">
        <h1>Study session unavailable</h1>
        <p role="alert">
          {error || "This study session could not be found."}
        </p>
        <Link to="/dashboard">Return to dashboard</Link>
      </main>
    );
  }

  const summary = session.summary;

  const noteSections = Array.isArray(session.notes)
    ? session.notes
    : session.notes?.sections || [];

  return (
    <div className="study-workspace">
      <aside className="study-workspace__sidebar">
        <p className="eyebrow">YOUR LIBRARY</p>
        <h2>Study history</h2>
        <p className="study-sidebar__description">
          Pick up where you left off.
        </p>

        <Link
          to="/dashboard"
          className="button button--primary study-sidebar__new"
        >
          + New video
        </Link>

        <div className="study-sidebar__sessions">
          {sessions.map((item) => (
            <button
              type="button"
              key={item.id}
              className={`study-sidebar__session ${
                item.id === sessionId
                  ? "study-sidebar__session--active"
                  : ""
              }`}
              onClick={() => navigate(`/study/${item.id}`)}
            >
              <span className="study-sidebar__session-title">
                {item.title || `Video ${item.video_id}`}
              </span>

              <span className="study-sidebar__session-language">
                {item.original_language || "Language unknown"}
              </span>

              <span className="study-sidebar__session-date">
                {formatDate(item.created_at || item.updated_at)}
              </span>
            </button>
          ))}
        </div>
      </aside>

      <main className="study-workspace__main">
        <header className="study-hero">
          <p className="eyebrow">YOUR LEARNING DESK</p>

          <h1>
            {session.title || "Your study session"}
          </h1>

          <p className="study-hero__description">
            Revisit important ideas, make useful notes, and
            ask questions as you learn.
          </p>

          <div className="study-hero__meta">
            <span>
              {session.original_language || "Language unknown"}
            </span>

            <a
              href={session.video_url}
              target="_blank"
              rel="noreferrer"
            >
              Open YouTube video ↗
            </a>
          </div>
        </header>

        <section className="study-card">
          <p className="eyebrow">YOUR STUDY TOOLS</p>
          <h2>Learn at your own pace.</h2>
          <p>
            Create a summary or structured notes from this video.
          </p>

          <div className="study-tools">
            <button
              type="button"
              className="button button--primary"
              onClick={handleGenerateSummary}
              disabled={summaryLoading}
            >
              {summaryLoading
                ? "Generating summary..."
                : summary
                  ? "Regenerate summary"
                  : "Generate summary"}
            </button>

            <button
              type="button"
              className="button button--secondary"
              onClick={handleGenerateNotes}
              disabled={notesLoading}
            >
              {notesLoading
                ? "Generating notes..."
                : noteSections.length > 0
                  ? "Regenerate notes"
                  : "Generate notes"}
            </button>
          </div>

          {summaryError && (
            <p className="form-error" role="alert">
              {summaryError}
            </p>
          )}

          {notesError && (
            <p className="form-error" role="alert">
              {notesError}
            </p>
          )}
        </section>

        {summaryLoading && (
          <p className="page-feedback">
            Your summary is being prepared...
          </p>
        )}

        {summary && (
          <section className="study-card study-content">
            <p className="eyebrow">VIDEO SUMMARY</p>
            <h2>Key ideas to remember</h2>

            <h3>Overview</h3>
            <p>{summary.overview}</p>

            <h3>Key points</h3>
            {summary.key_points?.length > 0 ? (
              <ul>
                {summary.key_points.map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
              </ul>
            ) : (
              <p>No key points available.</p>
            )}

            <h3>Key concepts</h3>
            {summary.concepts?.length > 0 ? (
              summary.concepts.map((concept, index) => (
                <article key={index}>
                  <h4>{concept.title}</h4>
                  <p>{concept.explanation}</p>
                </article>
              ))
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
          </section>
        )}

        {notesLoading && (
          <p className="page-feedback">
            Your study notes are being prepared...
          </p>
        )}

        {noteSections.length > 0 && (
          <section className="study-card study-content">
            <p className="eyebrow">YOUR NOTES</p>
            <h2>Notes worth keeping</h2>

            {noteSections.map((section, index) => (
              <article
                className="study-note"
                key={`${section.timestamp}-${index}`}
              >
                <h3>{section.title}</h3>

                {typeof section.timestamp === "number" && (
                  <p className="study-note__timestamp">
                    Timestamp:{" "}
                    {Math.floor(section.timestamp / 60)}:
                    {String(
                      Math.floor(section.timestamp % 60)
                    ).padStart(2, "0")}
                  </p>
                )}

                {section.points?.length > 0 ? (
                  <ul>
                    {section.points.map((point, pointIndex) => (
                      <li key={pointIndex}>{point}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No points available in this section.</p>
                )}
              </article>
            ))}
          </section>
        )}

        <section className="study-card">
          <p className="eyebrow">READ AND REVISIT</p>
          <h2>Transcript</h2>

          <div className="study-transcript__meta">
            <span>
              Original language:{" "}
              {session.original_language || "Unknown"}
            </span>
            <span>
              {session.english_transcript?.length || 0} English segments
            </span>
          </div>

          <TranscriptViewer
            originalTranscript={session.original_transcript}
            englishTranscript={session.english_transcript}
          />
        </section>

        <section className="study-card">
          <p className="eyebrow">EXPLORE FURTHER</p>
          <h2>Ask about this video.</h2>
          <p>
            Ask a question about the ideas or details covered
            in the video.
          </p>

          <ChatPanel videoId={session.video_id} />
        </section>
      </main>
    </div>
  );
}

export default StudySession;

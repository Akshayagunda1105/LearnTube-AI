
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import VideoInput from "../components/VideoInput";

function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const loadSessions = async () => {
      try {
        const response = await api.get("/api/study-sessions");
        setSessions(response.data);
      } catch (err) {
        console.error(err);

        const detail = err.response?.data?.detail;
        setError(
          typeof detail === "string"
            ? detail
            : "Could not load study sessions."
        );
      } finally {
        setLoading(false);
      }
    };

    loadSessions();
  }, []);

  const formatDate = (dateValue) => {
    if (!dateValue) return "Date unavailable";

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
      return "Date unavailable";
    }

    return date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <main className="workspace">
      <aside className="workspace-sidebar">
        <div className="workspace-sidebar__heading">
          <p className="eyebrow">YOUR LIBRARY</p>
          <h2>Study history</h2>
          <p>Pick up where you left off.</p>
        </div>

        <button
          type="button"
          className="button button--secondary workspace-sidebar__new"
          onClick={() => navigate("/dashboard")}
        >
          + New video
        </button>

        {loading && (
          <p className="page-feedback">Loading sessions...</p>
        )}

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}

        {!loading && !error && sessions.length === 0 && (
          <p className="workspace-sidebar__empty">
            Your previous sessions will appear here.
          </p>
        )}

        {!loading && !error && sessions.length > 0 && (
          <div className="workspace-sidebar__sessions">
            {sessions.map((session) => (
              <button
                type="button"
                className="history-item"
                key={session.id}
                onClick={() => navigate(`/study/${session.id}`)}
              >
                <span className="history-item__title">
                  {session.title || `Video ${session.video_id}`}
                </span>

                <span className="history-item__meta">
                  {session.original_language || "Unknown language"}
                </span>

                <span className="history-item__date">
                  {formatDate(session.created_at || session.updated_at)}
                </span>
              </button>
            ))}
          </div>
        )}
      </aside>

      <section className="workspace-main">
        <header className="workspace-intro">
          <p className="eyebrow">YOUR LEARNING DESK</p>
          <h1>
            What shall we learn
            <br />
            <span className="dashboard-intro__accent">
              today?
            </span>
          </h1>
          <p>
            Turn YouTube videos into useful notes, clear summaries,
            and conversations that help ideas stick.
          </p>
        </header>

        <section className="workspace-video">
          <div className="section-heading">
            <span className="section-heading__number">01</span>
            <div>
              <h2>Start with a video</h2>
              <p>Bring something interesting to your study desk.</p>
            </div>
          </div>

          <VideoInput />
        </section>

        <section className="workspace-placeholder">
          <p className="eyebrow">YOUR STUDY TOOLS</p>
          <h2>Learn at your own pace.</h2>
          <p>
            Process a video to open its study session, where you can
            generate AI summaries and notes, explore the transcript,
            and ask questions about the video.
          </p>
        </section>
      </section>
    </main>
  );
}

export default Dashboard;

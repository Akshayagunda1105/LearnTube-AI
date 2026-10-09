
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

        if (typeof detail === "string") {
          setError(detail);
        } else {
          setError("Could not load study sessions.");
        }
      } finally {
        setLoading(false);
      }
    };

    loadSessions();
  }, []);

  const formatDate = (dateValue) => {
    if (!dateValue) {
      return "Date unavailable";
    }

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

  const openSession = (sessionId) => {
    navigate(`/study/${sessionId}`);
  };

  return (
    <div>
      <h1>Dashboard</h1>

      <VideoInput />

      <section>
        <h2>Study History</h2>

        {loading && <p>Loading study sessions...</p>}

        {error && <p role="alert">{error}</p>}

        {!loading && !error && (
          <>
            <p>
              You have {sessions.length} study{" "}
              {sessions.length === 1 ? "session" : "sessions"}.
            </p>

            {sessions.length === 0 ? (
              <p>
                No study sessions yet. Process a YouTube video
                above to get started.
              </p>
            ) : (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(260px, 1fr))",
                  gap: "20px",
                  marginTop: "20px",
                }}
              >
                {sessions.map((session) => (
                  <article
                    key={session.id}
                    style={{
                      border: "1px solid #ccc",
                      borderRadius: "8px",
                      padding: "16px",
                    }}
                  >
                    {session.thumbnail && (
                      <img
                        src={session.thumbnail}
                        alt={session.title || "YouTube video thumbnail"}
                        style={{
                          width: "100%",
                          borderRadius: "6px",
                          marginBottom: "12px",
                        }}
                      />
                    )}

                    <h3>
                      {session.title || `Video ${session.video_id}`}
                    </h3>

                    <p>
                      <strong>Language:</strong>{" "}
                      {session.original_language || "Unknown"}
                    </p>

                    <p>
                      <strong>Studied on:</strong>{" "}
                      {formatDate(
                        session.created_at || session.updated_at
                      )}
                    </p>

                    <button
                      type="button"
                      onClick={() => openSession(session.id)}
                    >
                      Reopen Study Session
                    </button>
                  </article>
                ))}
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}

export default Dashboard;

import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

  return (
    <div>
      <h1>Dashboard</h1>

      {loading && <p>Loading study sessions...</p>}

      {error && <p>{error}</p>}

      {!loading && !error && (
        <div>
          <p>Study sessions loaded: {sessions.length}</p>

          {sessions.length === 0 && (
            <p>No study sessions yet.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
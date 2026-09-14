import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const testBackendConnection = async () => {
      try {
        const response = await api.get("/api/test");
        setMessage(response.data.message);
      } catch (err) {
        console.error(err);
        setError("Could not connect to the backend.");
      } finally {
        setLoading(false);
      }
    };

    testBackendConnection();
  }, []);

  return (
    <div>
      <h1>LearnTube AI</h1>

      <h2>Backend Connection</h2>

      {loading && <p>Connecting to backend...</p>}

      {message && <p>{message}</p>}

      {error && <p>{error}</p>}
    </div>
  );
}

export default App;
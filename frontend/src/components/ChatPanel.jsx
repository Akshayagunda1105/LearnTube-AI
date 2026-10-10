
import { useEffect, useState } from "react";
import api from "../services/api";

function formatTimestamp(seconds) {
  const totalSeconds = Math.floor(seconds || 0);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const remainingSeconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  }

  return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
}

function ChatPanel({ sessionId, videoId }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadChatHistory() {
      setMessages([]);
      setError("");

      try {
        const response = await api.get(
          `/api/study-sessions/${sessionId}`
        );

        if (!cancelled) {
          setMessages(response.data.chat_history || []);
        }
      } catch (err) {
        if (!cancelled) {
          console.error(err);
          setError("Could not load previous chat messages.");
        }
      }
    }

    if (sessionId) {
      loadChatHistory();
    }

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading || !sessionId) {
      return;
    }

    const history = messages.map((message) => ({
      role: message.role,
      content: message.content,
    }));

    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const response = await api.post("/api/chat", {
        session_id: sessionId,
        video_id: videoId,
        question: trimmedQuestion,
        history,
      });

      const updatedSession = await api.get(
        `/api/study-sessions/${sessionId}`
      );

      setMessages(updatedSession.data.chat_history || []);
    } catch (err) {
      console.error(err);

      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Could not get an answer. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Ask AI About This Video</h2>

      <p>
        Ask questions about the video and use follow-up questions
        to clarify or shorten previous answers.
      </p>

      <div aria-live="polite">
        {messages.map((message, index) => (
          <article key={`${message.role}-${index}`}>
            <h3>
              {message.role === "user" ? "You" : "AI Assistant"}
            </h3>

            <p style={{ whiteSpace: "pre-wrap" }}>
              {message.content}
            </p>

            {message.role === "assistant" &&
              message.sources?.length > 0 && (
                <div>
                  <h4>Transcript Sources</h4>

                  {message.sources.map((source, sourceIndex) => (
                    <div
                      key={`${source.start}-${sourceIndex}`}
                      style={{
                        borderLeft: "3px solid #888",
                        paddingLeft: "12px",
                        marginBottom: "12px",
                      }}
                    >
                      <p>
                        <strong>
                          {formatTimestamp(source.start)}
                          {" – "}
                          {formatTimestamp(source.end)}
                        </strong>
                      </p>

                      <p>{source.text}</p>
                    </div>
                  ))}
                </div>
              )}
          </article>
        ))}
      </div>

      {loading && <p>AI is thinking...</p>}

      {error && <p role="alert">{error}</p>}

      <form onSubmit={handleSubmit}>
        <label htmlFor="chat-question">Your question</label>

        <textarea
          id="chat-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask something about this video..."
          rows={3}
          disabled={loading}
          required
          style={{
            display: "block",
            width: "100%",
            maxWidth: "600px",
            marginTop: "8px",
            marginBottom: "12px",
          }}
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
        >
          {loading ? "Getting Answer..." : "Ask AI"}
        </button>
      </form>
    </section>
  );
}

export default ChatPanel;

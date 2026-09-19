import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function VideoInput() {
  const navigate = useNavigate();

  const [videoUrl, setVideoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!videoUrl.trim()) {
      setError("Please enter a YouTube video URL.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/api/videos/process", {
        video_id: extractVideoId(videoUrl),
        video_url: videoUrl.trim(),
      });

      const sessionId = response.data.session_id;

      if (!sessionId) {
        throw new Error("Study session ID was not returned.");
      }

      navigate(`/study/${sessionId}`);
    } catch (err) {
      console.error(err);

      const detail = err.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Failed to process the video. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const extractVideoId = (url) => {
    try {
      const parsedUrl = new URL(url);

      if (parsedUrl.hostname.includes("youtube.com")) {
        return parsedUrl.searchParams.get("v") || "";
      }

      if (parsedUrl.hostname === "youtu.be") {
        return parsedUrl.pathname.slice(1);
      }

      return "";
    } catch {
      return "";
    }
  };

  return (
    <div>
      <h2>Learn from a YouTube Video</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={videoUrl}
          onChange={(event) => setVideoUrl(event.target.value)}
          placeholder="Paste a YouTube video URL"
        />

        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Start Learning"}
        </button>
      </form>

      {error && <p>{error}</p>}
    </div>
  );
}

export default VideoInput;
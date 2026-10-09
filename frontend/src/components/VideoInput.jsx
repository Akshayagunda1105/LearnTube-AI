
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function VideoInput({ onProcessed }) {
  const navigate = useNavigate();

  const [videoUrl, setVideoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const extractVideoId = (url) => {
    try {
      const parsedUrl = new URL(url);

      if (
        parsedUrl.hostname === "youtube.com" ||
        parsedUrl.hostname.endsWith(".youtube.com")
      ) {
        return parsedUrl.searchParams.get("v") || "";
      }

      if (
        parsedUrl.hostname === "youtu.be" ||
        parsedUrl.hostname.endsWith(".youtu.be")
      ) {
        return parsedUrl.pathname.slice(1);
      }

      return "";
    } catch {
      return "";
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    const trimmedUrl = videoUrl.trim();
    const videoId = extractVideoId(trimmedUrl);

    if (!videoId) {
      setError("Please enter a valid YouTube video URL.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/api/videos/process", {
        video_id: videoId,
        video_url: trimmedUrl,
      });

      const sessionId = response.data.session_id;

      if (!sessionId) {
        throw new Error("Study session ID was not returned.");
      }

      setVideoUrl("");

      if (onProcessed) {
        onProcessed({
          sessionId,
          videoId,
          videoUrl: trimmedUrl,
        });
      } else {
        // Preserve the existing behavior on pages
        // that don't supply an onProcessed callback.
        navigate(`/study/${sessionId}`);
      }
    } catch (err) {
      console.error(err);

      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : err.message === "Study session ID was not returned."
            ? err.message
            : "Failed to process the video. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="video-input">
      <form onSubmit={handleSubmit} className="video-input__form">
        <label htmlFor="youtube-url">
          YouTube video URL
        </label>

        <div className="video-input__controls">
          <input
            id="youtube-url"
            type="url"
            value={videoUrl}
            onChange={(event) => setVideoUrl(event.target.value)}
            placeholder="Paste a YouTube video URL"
            required
          />

          <button
            type="submit"
            className="button button--primary"
            disabled={loading}
          >
            {loading ? "Processing video..." : "Process video"}
          </button>
        </div>
      </form>

      {loading && (
        <p className="video-input__status" role="status">
          Fetching the transcript and preparing your study session...
        </p>
      )}

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}

export default VideoInput;

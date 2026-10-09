
import { useState } from "react";

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

function TranscriptViewer({ originalTranscript = [], englishTranscript = [] }) {
  const [language, setLanguage] = useState("english");

  const transcript =
    language === "english" ? englishTranscript : originalTranscript;

  return (
    <section>
      <h2>Transcript</h2>

      <label htmlFor="transcript-language">Transcript language: </label>
      <select
        id="transcript-language"
        value={language}
        onChange={(event) => setLanguage(event.target.value)}
      >
        <option value="english">English</option>
        <option value="original">Original language</option>
      </select>

      {transcript.length === 0 ? (
        <p>No transcript is available for this language.</p>
      ) : (
        <div
          style={{
            maxHeight: "400px",
            overflowY: "auto",
            border: "1px solid #ccc",
            padding: "12px",
            marginTop: "12px",
          }}
        >
          {transcript.map((segment, index) => (
            <div
              key={`${segment.start}-${index}`}
              style={{
                display: "flex",
                gap: "12px",
                marginBottom: "12px",
              }}
            >
              <span style={{ minWidth: "60px", fontWeight: "bold" }}>
                {formatTimestamp(segment.start)}
              </span>

              <span>{segment.text}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default TranscriptViewer;

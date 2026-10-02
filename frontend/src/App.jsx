import { useEffect, useRef, useState } from "react";
import { askQuestion, uploadDocument } from "./api";
import "./App.css";

function friendly(error) {
  // "Failed to fetch" means the backend couldn't be reached at all
  return error instanceof TypeError
    ? "Can't reach the server. Is the backend running?"
    : error.message;
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [thinking, setThinking] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const bottomRef = useRef(null);

  // keep the newest message in view
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  async function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    setUploadStatus(`Uploading ${file.name}...`);
    try {
      const result = await uploadDocument(file);
      setUploadStatus(`✅ ${result.filename} added (${result.chunks} pieces)`);
    } catch (error) {
      setUploadStatus(`❌ ${friendly(error)}`);
    }
    event.target.value = ""; // allow picking the same file again
  }

  async function handleSend(event) {
    event.preventDefault();
    const text = question.trim();
    if (!text || thinking) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setQuestion("");
    setThinking(true);

    try {
      const result = await askQuestion(text);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: result.answer, sources: result.sources },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: friendly(error), sources: [], isError: true },
      ]);
    } finally {
      setThinking(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>📚 Ask My Docs</h1>
        <label className="upload-button">
          Upload a document
          <input
            type="file"
            accept=".txt,.md,.pdf"
            onChange={handleUpload}
            hidden
          />
        </label>
      </header>

      {uploadStatus && <p className="upload-status">{uploadStatus}</p>}

      <main className="chat">
        {messages.length === 0 && (
          <p className="hint">
            Upload a .txt, .md or .pdf file, then ask a question about it.
          </p>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`bubble ${message.role}${message.isError ? " error" : ""}`}
          >
            <p>{message.text}</p>
            {message.sources?.length > 0 && (
              <details>
                <summary>Sources ({message.sources.length})</summary>
                {message.sources.map((source, i) => (
                  <div key={i} className="source">
                    <strong>{source.source}</strong>
                    <span className="score">
                      {" "}
                      match {source.score.toFixed(2)}
                    </span>
                    <p>{source.text}…</p>
                  </div>
                ))}
              </details>
            )}
          </div>
        ))}

        {thinking && <div className="bubble bot">Thinking…</div>}
        <div ref={bottomRef} />
      </main>

      <form className="composer" onSubmit={handleSend}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask something about your documents…"
        />
        <button type="submit" disabled={thinking || !question.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

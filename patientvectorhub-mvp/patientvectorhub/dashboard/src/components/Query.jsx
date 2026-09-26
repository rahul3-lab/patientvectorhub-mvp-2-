import { useState } from "react";
import { askQuestion } from "../api.js";

export default function Query() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleAsk() {
    if (!question.trim()) return;
    setBusy(true);
    setError("");
    setAnswer(null);
    try {
      const result = await askQuestion(question);
      setAnswer(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2>Ask a question</h2>
      <textarea
        rows={3}
        style={{ width: "100%", maxWidth: 500 }}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="e.g. What medications were listed in the last visit note?"
      />
      <div>
        <button onClick={handleAsk} disabled={busy}>
          {busy ? "Thinking..." : "Ask"}
        </button>
      </div>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {answer && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Answer</h3>
          <p>{answer.answer}</p>

          {answer.sources?.length > 0 && (
            <>
              <h4>Sources</h4>
              <ul>
                {answer.sources.map((s, i) => (
                  <li key={i}>
                    doc {s.document_id?.slice(0, 8)}… chunk #{s.chunk_index} (score {s.score?.toFixed(3)})
                    <br />
                    <em>{s.excerpt}</em>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

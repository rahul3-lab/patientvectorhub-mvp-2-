import { useState } from "react";
import { uploadDocument, getDocumentStatus } from "../api.js";

export default function Upload({ onIngested }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleUpload() {
    if (!file) return;
    setBusy(true);
    setStatus("Uploading...");
    try {
      const { document_id } = await uploadDocument(file);
      setStatus("Processing (parsing → embedding)...");

      // Simple poll loop - MVP has no websocket/SSE push.
      for (let i = 0; i < 30; i++) {
        await new Promise((r) => setTimeout(r, 2000));
        const doc = await getDocumentStatus(document_id);
        if (doc.status === "ready") {
          setStatus(`Ready - ${doc.chunk_count} chunks indexed.`);
          onIngested?.();
          break;
        }
        if (doc.status === "failed") {
          setStatus(`Failed: ${doc.error_message}`);
          break;
        }
        setStatus(`Status: ${doc.status}...`);
      }
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ marginBottom: "2rem" }}>
      <h2>Upload a document</h2>
      <input type="file" accept=".pdf,.txt,.md" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={!file || busy} style={{ marginLeft: "0.5rem" }}>
        {busy ? "Working..." : "Upload"}
      </button>
      {status && <p>{status}</p>}
    </div>
  );
}

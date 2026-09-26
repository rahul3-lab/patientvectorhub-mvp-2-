import { useState, useEffect } from "react";
import Upload from "./components/Upload.jsx";
import Query from "./components/Query.jsx";
import { listDocuments } from "./api.js";

export default function App() {
  const [docs, setDocs] = useState([]);

  async function refresh() {
    try {
      setDocs(await listDocuments());
    } catch {
      // gateway not reachable yet - fine on first load
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 700, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>PatientVectorHub</h1>
      <p style={{ color: "#666" }}>MVP dashboard - upload a document, then ask questions about it.</p>

      <Upload onIngested={refresh} />

      <div style={{ marginBottom: "2rem" }}>
        <h2>Documents ({docs.length})</h2>
        <ul>
          {docs.map((d) => (
            <li key={d.document_id}>
              {d.filename} - <strong>{d.status}</strong>
            </li>
          ))}
        </ul>
      </div>

      <Query />
    </div>
  );
}

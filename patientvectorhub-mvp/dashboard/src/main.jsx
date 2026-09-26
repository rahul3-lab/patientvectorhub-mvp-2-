import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const headers = tenant => ({ 'Content-Type': 'application/json', 'X-Tenant-ID': tenant });

function App() {
  const [tenant, setTenant] = useState('demo-clinic');
  const [patient, setPatient] = useState('patient-001');
  const [filename, setFilename] = useState('clinical-note.txt');
  const [content, setContent] = useState('Patient reports improved sleep and no adverse effects after the medication adjustment. Follow up is planned in two weeks.');
  const [question, setQuestion] = useState('What does the note say about follow up?');
  const [status, setStatus] = useState('Ready');
  const [answer, setAnswer] = useState(null);
  const upload = async e => {
    e.preventDefault(); setStatus('Indexing document…');
    try { const r = await fetch(`${API}/v1/documents`, { method: 'POST', headers: headers(tenant), body: JSON.stringify({patient_id: patient, filename, content}) }); const data = await r.json(); if (!r.ok) throw new Error(data.detail || 'Upload failed'); setStatus(`Indexed ${data.chunks_indexed} chunk(s).`); } catch (err) { setStatus(err.message); }
  };
  const ask = async e => {
    e.preventDefault(); setStatus('Retrieving context…'); setAnswer(null);
    try { const r = await fetch(`${API}/v1/query`, { method: 'POST', headers: headers(tenant), body: JSON.stringify({patient_id: patient, question}) }); const data = await r.json(); if (!r.ok) throw new Error(data.detail || 'Query failed'); setAnswer(data); setStatus('Answer ready.'); } catch (err) { setStatus(err.message); }
  };
  return <main><header><p className="eyebrow">PATIENTVECTORHUB / DEVELOPMENT</p><h1>Patient document intelligence</h1><p>Securely scope documents and answers to a tenant and patient record.</p></header><section className="identity"><label>Tenant ID<input value={tenant} onChange={e => setTenant(e.target.value)} /></label><label>Patient ID<input value={patient} onChange={e => setPatient(e.target.value)} /></label></section><div className="grid"><form onSubmit={upload}><h2>Index a document</h2><label>Filename<input value={filename} onChange={e => setFilename(e.target.value)} /></label><label>Document text<textarea value={content} onChange={e => setContent(e.target.value)} /></label><button>Index document</button></form><form onSubmit={ask}><h2>Ask the record</h2><label>Question<textarea value={question} onChange={e => setQuestion(e.target.value)} /></label><button>Retrieve answer</button>{answer && <article><p>{answer.answer}</p><small>{answer.disclaimer}</small><h3>Sources</h3>{answer.citations.map(c => <div className="citation" key={c.document_id + c.excerpt}><b>{c.filename}</b> · {c.score}<br />{c.excerpt}</div>)}</article>}</form></div><footer>{status}</footer></main>;
}
createRoot(document.getElementById('root')).render(<App />);

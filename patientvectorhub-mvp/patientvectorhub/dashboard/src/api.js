// MVP auth: shared secret + tenant name. No login UI - both are hardcoded
// here for local dev. Replace with real auth once Keycloak is reintroduced.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const SHARED_SECRET = import.meta.env.VITE_API_SHARED_SECRET || "change-me-local-dev-secret";
const TENANT_ID = import.meta.env.VITE_TENANT_NAME || "demo-tenant";

function headers(extra = {}) {
  return {
    Authorization: `Bearer ${SHARED_SECRET}`,
    "X-Tenant-Id": TENANT_ID,
    ...extra,
  };
}

export async function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    headers: headers(),
    body: form,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

export async function getDocumentStatus(documentId) {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, { headers: headers() });
  if (!res.ok) throw new Error(`Status check failed: ${res.status}`);
  return res.json();
}

export async function listDocuments() {
  const res = await fetch(`${API_BASE}/documents`, { headers: headers() });
  if (!res.ok) throw new Error(`List failed: ${res.status}`);
  return res.json();
}

export async function askQuestion(question) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Query failed: ${res.status}`);
  return res.json();
}

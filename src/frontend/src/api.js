const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
  } catch {
    throw new Error("API unreachable — is the FastAPI server running?");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail) ? detail.map((d) => d.msg || d).join(", ") : detail || res.statusText;
    throw new Error(message || `Request failed (${res.status})`);
  }
  return data;
}

export const api = {
  health: () => request("/health"),
  tasks: () => request("/tasks"),
  predict: (task, features) =>
    request(`/predict/${task}`, { method: "POST", body: JSON.stringify({ features }) }),
  metrics: (task) => request(`/models/${task}/metrics`),
};

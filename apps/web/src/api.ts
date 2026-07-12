const API_BASE = import.meta.env.VITE_ATLAS_API_BASE_URL || '/api/v1';

let authToken = '';

export function setAuthToken(token: string) {
  authToken = token;
}

function authHeaders(): Record<string, string> {
  if (authToken) return { 'Authorization': `Bearer ${authToken}` };
  return {};
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.detail || err.error || res.statusText);
  }
  const data = await res.json();
  return data.data ?? data;
}

export const api = {
  health: () => request<{ status: string; version: string; first_run?: boolean }>('/health'),
  ready: () => request('/ready'),

  register: (email: string, password: string, display_name?: string) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, display_name }) }),
  login: (email: string, password: string) =>
    request<{ access_token: string; expires_at: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  getMe: () => request<{ authenticated: boolean; user_id?: string; email?: string; display_name?: string }>('/auth/me'),
  setAuthToken,

  listProjects: (userId = 'local-user') =>
    request<{ projects: any[] }>(`/projects?user_id=${userId}`),
  getProject: (id: string) => request(`/projects/${id}`),
  createProject: (name: string, description = '', userId = 'local-user') =>
    request('/projects', { method: 'POST', body: JSON.stringify({ name, description, user_id: userId }) }),
  deleteProject: (id: string) =>
    request(`/projects/${id}`, { method: 'DELETE' }),

  listDocuments: (projectId: string) =>
    request<{ documents: any[] }>(`/projects/${projectId}/documents`),
  getDocument: (id: string) => request(`/documents/${id}`),
  getDocumentChunks: (id: string) => request<{ chunks: any[] }>(`/documents/${id}/chunks`),

  createResearchSession: (projectId: string, title: string, query: string, model = 'gpt-4') =>
    request<{ session_id: string; status: string }>('/research-sessions', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, user_id: 'local-user', title, query, model }),
    }),
  getResearchSession: (id: string) => request(`/research-sessions/${id}`),
  listResearchSessions: (projectId: string) =>
    request<{ sessions: any[] }>(`/projects/${projectId}/research-sessions`),
  chat: (sessionId: string, message: string, apiKey = '') =>
    request<{ response: string; messages: any[] }>(`/research-sessions/${sessionId}/chat`, {
      method: 'POST', body: JSON.stringify({ message, api_key: apiKey }),
    }),
  runResearch: (sessionId: string, apiKey = '') =>
    request<{ status: string; analysis: string; search_results_count: number }>(
      `/research-sessions/${sessionId}/research`, { method: 'POST', body: JSON.stringify({ api_key: apiKey }) }
    ),
  generateReport: (sessionId: string) =>
    request(`/research-sessions/${sessionId}/generate-report`, { method: 'POST' }),
  getReport: (sessionId: string) => request(`/research-sessions/${sessionId}/report`),
  deleteResearchSession: (id: string) =>
    request(`/research-sessions/${id}`, { method: 'DELETE' }),

  search: (query: string, limit = 10) =>
    request<{ results: any[] }>(`/search?query=${encodeURIComponent(query)}&limit=${limit}`),

  listEvidence: (sessionId: string) =>
    request<{ evidence: any[] }>(`/research-sessions/${sessionId}/evidence`),

  saveResearch: (projectId: string, researchSessionId: string, title: string, summary = '') =>
    request(`/projects/${projectId}/research`, {
      method: 'POST',
      body: JSON.stringify({ research_session_id: researchSessionId, title, summary }),
    }),
  listSavedResearch: (projectId: string) =>
    request<{ saved_research: any[] }>(`/projects/${projectId}/research`),

  exportMarkdown: (sessionId: string) => `${API_BASE}/export/${sessionId}/markdown`,
  exportJson: (sessionId: string) => `${API_BASE}/export/${sessionId}/json`,
  exportPdf: (sessionId: string) => `${API_BASE}/export/${sessionId}/pdf`,
  exportDocx: (sessionId: string) => `${API_BASE}/export/${sessionId}/docx`,

  getSettings: () => request<Record<string, string>>('/settings'),
  setSetting: (key: string, value: string) =>
    request('/settings', { method: 'POST', body: JSON.stringify({ key, value }) }),

  quickChat: (message: string, projectId?: string, sessionId?: string, apiKey?: string) =>
    request<{ project_id: string; session_id: string; response: string; messages: any[] }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, project_id: projectId, session_id: sessionId, api_key: apiKey }),
    }),

  listNotes: (projectId: string) => request<{ notes: any[] }>(`/projects/${projectId}/notes`),

  uploadDocument: (projectId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${API_BASE}/projects/${projectId}/documents/ingest`, {
      method: 'POST', headers: authHeaders(), body: formData,
    }).then(r => r.json());
  },
};

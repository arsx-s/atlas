import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Routes, Route, useNavigate, useLocation, Navigate, Link } from 'react-router-dom';
import { api } from './api';

type Section = 'chat' | 'research' | 'projects' | 'library' | 'reports' | 'settings';

interface BackendHealth {
  status: string;
  version?: string;
  environment?: string;
}

interface Project {
  project_id: string;
  name: string;
  description: string;
  created_at: string;
}

interface Document {
  document_id: string;
  title: string;
  file_name: string;
  file_format: string;
  file_size_bytes: number;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ResearchSession {
  session_id: string;
  project_id: string;
  title: string;
  query: string;
  status: string;
  messages: ChatMessage[];
  created_at: string;
}

interface UserInfo {
  authenticated: boolean;
  user_id?: string;
  email?: string;
  display_name?: string;
}

// --------------- Auth Context ---------------
const AuthContext = React.createContext<{
  user: UserInfo | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}>({
  user: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  loading: true,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('atlas_access_token');
    if (token) {
      api.setAuthToken(token);
      api.getMe().then(u => {
        if (u.authenticated) setUser(u);
        else localStorage.removeItem('atlas_access_token');
      }).catch(() => {
        localStorage.removeItem('atlas_access_token');
      }).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.login(email, password);
    localStorage.setItem('atlas_access_token', res.access_token);
    api.setAuthToken(res.access_token);
    const u = await api.getMe();
    setUser(u);
  };

  const register = async (email: string, password: string, name?: string) => {
    await api.register(email, password, name);
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('atlas_access_token');
    api.setAuthToken('');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return React.useContext(AuthContext);
}

// --------------- Sidebar ---------------
function Sidebar({ active, onNavigate, theme, onToggleTheme, backend, user, onLogout }: {
  active: Section; onNavigate: (s: Section) => void;
  theme: string; onToggleTheme: () => void; backend: BackendHealth;
  user: UserInfo | null; onLogout: () => void;
}) {
  const navigate = useNavigate();
  const nav = [
    { id: 'chat' as Section, label: 'Chat', desc: 'AI research assistant' },
    { id: 'research' as Section, label: 'Research', desc: 'Advanced research workspace' },
    { id: 'projects' as Section, label: 'Projects', desc: 'Manage projects' },
    { id: 'library' as Section, label: 'Library', desc: 'Documents & sources' },
    { id: 'reports' as Section, label: 'Reports', desc: 'Generated reports' },
    { id: 'settings' as Section, label: 'Settings', desc: 'Configuration' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1 className="sidebar-logo">Atlas</h1>
        <p className="sidebar-subtitle">AI research workspace</p>
      </div>
      <nav className="sidebar-nav" aria-label="Main navigation">
        {nav.map(item => (
          <button
            key={item.id}
            className={`nav-item ${active === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
            aria-current={active === item.id ? 'page' : undefined}
          >
            <span className="nav-label">{item.label}</span>
            <span className="nav-desc">{item.desc}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="status-pill" data-status={backend.status}>
          <span className="status-dot" />
          <span className="status-text">
            {backend.status === 'ok' ? `Connected v${backend.version || '0.1'}` : backend.status === 'checking' ? 'Connecting...' : 'Offline'}
          </span>
        </div>
        <button className="theme-toggle" onClick={onToggleTheme} aria-label="Toggle theme">
          {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
        </button>
        {user?.authenticated ? (
          <div className="user-info">
            <span className="user-email">{user.email}</span>
            <button className="btn btn-secondary btn-sm" onClick={onLogout}>Logout</button>
          </div>
        ) : (
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/login')}>Sign In</button>
        )}
      </div>
    </aside>
  );
}

// --------------- Login Page ---------------
function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-logo">Atlas</h1>
        <p className="auth-subtitle">Sign in to your workspace</p>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <label>Email
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required autoFocus />
          </label>
          <label>Password
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </label>
          <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="auth-footer">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}

// --------------- Register Page ---------------
function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(email, password, name || undefined);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-logo">Atlas</h1>
        <p className="auth-subtitle">Create your workspace</p>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <label>Display Name (optional)
            <input type="text" value={name} onChange={e => setName(e.target.value)} />
          </label>
          <label>Email
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </label>
          <label>Password
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />
          </label>
          <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

// --------------- Home View ---------------
function HomeView({ onNavigate }: { onNavigate: (s: Section) => void }) {
  const [prompt, setPrompt] = useState('');
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const { user } = useAuth();

  useEffect(() => {
    api.listProjects().then(d => setRecentProjects(d.projects || [])).catch(() => {});
  }, []);

  return (
    <div className="page home-page">
      <div className="hero-section">
        <h2 className="hero-title">What would you like to research?</h2>
        <div className="hero-prompt">
          <textarea
            className="prompt-input"
            placeholder="Describe your research topic or question..."
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            rows={3}
          />
          <div className="prompt-actions">
            <button className="btn btn-primary" disabled={!prompt.trim()} onClick={() => onNavigate('research')}>
              Start Research
            </button>
            <button className="btn btn-secondary" onClick={() => onNavigate('research')}>
              Continue Existing
            </button>
          </div>
        </div>
      </div>

      <div className="quick-search">
        <input className="search-input" placeholder="Quick search projects and documents..." disabled aria-label="Search (coming soon)" />
      </div>

      <div className="feature-grid">
        <div className="feature-card" onClick={() => onNavigate('projects')}>
          <h3>Projects</h3>
          <p>Organize research into projects with notes, documents, and saved findings.</p>
          {recentProjects.length > 0 && (
            <span className="feature-count">{recentProjects.length} projects</span>
          )}
        </div>
        <div className="feature-card" onClick={() => onNavigate('library')}>
          <h3>Documents</h3>
          <p>Upload PDFs, DOCX, and markdown files. Search and analyze content.</p>
        </div>
        <div className="feature-card" onClick={() => onNavigate('reports')}>
          <h3>Reports</h3>
          <p>Generate comprehensive research reports with citations and evidence.</p>
        </div>
      </div>

      <div className="recent-section">
        <h3>Recent Projects</h3>
        {recentProjects.length === 0 ? (
          <div className="empty-state">
            <p>No projects yet. Create your first project to get started.</p>
          </div>
        ) : (
          <div className="project-list">
            {recentProjects.slice(0, 5).map(p => (
              <div key={p.project_id} className="project-card-small">
                <h4>{p.name}</h4>
                <p>{p.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// --------------- Chat View ---------------
function ChatView() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState<'idle' | 'creating' | 'thinking'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(() => localStorage.getItem('atlas-active-project-id'));
  const [activeSessionId, setActiveSessionId] = useState<string | null>(() => localStorage.getItem('atlas-active-session-id'));
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('atlas-chat-messages');
    if (saved) { try { setMessages(JSON.parse(saved)); } catch {} }
  }, []);

  useEffect(() => {
    if (activeProjectId) {
      api.listResearchSessions(activeProjectId).then(d => setSessions(d.sessions || [])).catch(() => {});
    } else {
      setSessions([]);
    }
  }, [activeProjectId]);

  useEffect(() => {
    if (activeSessionId) {
      api.getResearchSession(activeSessionId).then(s => { if (s.messages) setMessages(s.messages); }).catch(() => {});
    }
  }, [activeSessionId]);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const persist = (pid: string | null, sid: string | null, msgs: ChatMessage[]) => {
    if (pid !== null) localStorage.setItem('atlas-active-project-id', pid);
    if (sid !== null) localStorage.setItem('atlas-active-session-id', sid);
    localStorage.setItem('atlas-chat-messages', JSON.stringify(msgs));
  };

  const sendMessage = async () => {
    if (!input.trim() || loading !== 'idle') return;
    const text = input.trim();
    const userMsg: ChatMessage = { role: 'user', content: text, timestamp: new Date().toISOString() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    persist(activeProjectId, activeSessionId, newMessages);
    if (!activeSessionId) {
      setLoading('creating');
      setError(null);
      try {
        const res = await api.quickChat(text);
        setActiveProjectId(res.project_id);
        setActiveSessionId(res.session_id);
        setMessages(res.messages || []);
        persist(res.project_id, res.session_id, res.messages || []);
        const d = await api.listResearchSessions(res.project_id);
        setSessions(d.sessions || []);
      } catch (err: any) {
        const errMsg = err.message || 'Failed to create workspace';
        setError(errMsg);
        setMessages(prev => prev.filter(m => m !== userMsg));
        persist(activeProjectId, activeSessionId, messages);
      } finally {
        setLoading('idle');
      }
    } else if (activeSessionId && activeProjectId) {
      setLoading('thinking');
      setError(null);
      try {
        const res = await api.quickChat(text, activeProjectId, activeSessionId);
        setMessages(res.messages || []);
        persist(activeProjectId, activeSessionId, res.messages || []);
      } catch (err: any) {
        const errMsg = err.message || 'Failed to send message';
        setError(errMsg);
        setMessages(prev => prev.filter(m => m !== userMsg));
        persist(activeProjectId, activeSessionId, messages);
      } finally {
        setLoading('idle');
      }
    }
  };

  const loadSession = (session: ResearchSession) => {
    setActiveSessionId(session.session_id);
    setActiveProjectId(session.project_id);
    setMessages(session.messages || []);
    setError(null);
    persist(session.project_id, session.session_id, session.messages || []);
  };

  const newChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setError(null);
    localStorage.removeItem('atlas-active-session-id');
    localStorage.removeItem('atlas-chat-messages');
  };

  return (
    <div className="page chat-page">
      <div className="chat-layout">
        <div className="chat-sidebar">
          <div className="chat-sidebar-header">
            <h4>Conversations</h4>
            <button className="btn btn-secondary btn-sm" onClick={newChat}>+ New</button>
          </div>
          {sessions.length === 0 ? (
            <div className="empty-state-sm"><p>No conversations yet</p></div>
          ) : (
            <div className="session-list">
              {sessions.map(s => (
                <button key={s.session_id} className={`session-item ${activeSessionId === s.session_id ? 'active' : ''}`}
                  onClick={() => loadSession(s)}>
                  <span className="session-title">{s.title}</span>
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="chat-main">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <h2 className="hero-title">What would you like to research?</h2>
              <p className="chat-empty-sub">Ask a question and I'll automatically create a workspace and start researching.</p>
              <div className="chat-empty-prompt">
                <textarea className="prompt-input" placeholder="Type your research question..." value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  rows={3} disabled={loading !== 'idle'} />
                <button className="btn btn-primary" onClick={sendMessage} disabled={!input.trim() || loading !== 'idle'}
                  style={{ alignSelf: 'flex-end' }}>
                  {loading === 'creating' ? 'Creating...' : 'Start Research'}
                </button>
              </div>
            </div>
          ) : (
            <div className="chat-messages-area">
              <div className="chat-messages">
                {messages.map((m, i) => (
                  <div key={i} className={`message message-${m.role}`}>
                    <div className="message-role">{m.role === 'user' ? 'You' : 'Atlas'}</div>
                    <div className="message-content">{m.content}</div>
                  </div>
                ))}
                {loading === 'thinking' && (
                  <div className="message message-assistant">
                    <div className="typing-indicator"><span /><span /><span /></div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
              {loading === 'creating' && <div className="creating-banner">Creating workspace...</div>}
              {error && <div className="error-banner">{error} <button className="btn btn-secondary btn-sm" onClick={() => setError(null)}>Dismiss</button></div>}
              <div className="chat-input-area">
                <textarea className="chat-input" placeholder="Ask a follow-up question..." value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  rows={2} disabled={loading !== 'idle'} />
                <div className="chat-actions">
                  <button className="btn btn-primary" onClick={sendMessage} disabled={!input.trim() || loading !== 'idle'}>
                    {loading === 'creating' ? 'Creating...' : loading === 'thinking' ? 'Thinking...' : 'Send'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// --------------- Research Page ---------------
function ResearchPage({ projectId: defaultProjectId }: { projectId?: string }) {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [activeSession, setActiveSession] = useState<ResearchSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [queryInput, setQueryInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionTitle, setSessionTitle] = useState('');
  const [projectId, setProjectId] = useState(defaultProjectId || '');
  const [projects, setProjects] = useState<Project[]>([]);
  const [evidence, setEvidence] = useState<any[]>([]);
  const [report, setReport] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'sources' | 'report'>('chat');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.listProjects().then(d => setProjects(d.projects || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (projectId) {
      api.listResearchSessions(projectId).then(d => setSessions(d.sessions || [])).catch(() => {});
    }
  }, [projectId]);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const loadSession = useCallback(async (session: ResearchSession) => {
    setActiveSession(session);
    setMessages(session.messages || []);
    setReport(null);
    setError('');
    try {
      const ev = await api.listEvidence(session.session_id);
      setEvidence(ev.evidence || []);
    } catch {}
  }, []);

  const createSession = async () => {
    setError('');
    if (!projectId) { setError('Please select a project.'); return; }
    if (!sessionTitle.trim()) { setError('Please enter a session title.'); return; }
    if (!queryInput.trim()) { setError('Please enter an initial research query.'); return; }
    setLoading(true);
    try {
      const res = await api.createResearchSession(projectId, sessionTitle, queryInput);
      const session: ResearchSession = {
        session_id: res.session_id,
        project_id: projectId,
        title: sessionTitle,
        query: queryInput,
        status: res.status,
        messages: [{ role: 'user', content: queryInput, timestamp: new Date().toISOString() }],
        created_at: new Date().toISOString(),
      };
      setSessions(prev => [session, ...prev]);
      setActiveSession(session);
      setMessages(session.messages);
      setSessionTitle('');
      setQueryInput('');
    } catch (err: any) {
      setError('Failed to create session: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!activeSession) { setError('No active session. Select or create a session first.'); return; }
    if (!input.trim()) { setError('Please enter a message.'); return; }
    setError('');
    const userMsg: ChatMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const res = await api.chat(activeSession.session_id, userMsg.content);
      setMessages(res.messages || []);
      const ev = await api.listEvidence(activeSession.session_id);
      setEvidence(ev.evidence || []);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}`, timestamp: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  };

  const runFullResearch = async () => {
    if (!activeSession) { setError('No active session. Select or create a session first.'); return; }
    setError('');
    setLoading(true);
    try {
      const res = await api.runResearch(activeSession.session_id);
      const ev = await api.listEvidence(activeSession.session_id);
      setEvidence(ev.evidence || []);
      setActiveTab('sources');
    } catch (err: any) {
      setError('Research failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const doGenerateReport = async () => {
    if (!activeSession) { setError('No active session. Select or create a session first.'); return; }
    setError('');
    setLoading(true);
    try {
      const res = await api.generateReport(activeSession.session_id);
      setReport(res);
      setActiveTab('report');
    } catch (err: any) {
      setError('Report generation failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page research-page">
      <div className="research-header">
        <h2>Research Workspace</h2>
        <div className="research-controls">
          <select className="select-input" value={projectId} onChange={e => { setProjectId(e.target.value); setError(''); }}>
            <option value="">Select project...</option>
            {projects.map(p => <option key={p.project_id} value={p.project_id}>{p.name}</option>)}
          </select>
          {!activeSession && (
            <div className="new-session-form">
              <input className="input" placeholder="Session title" value={sessionTitle} onChange={e => { setSessionTitle(e.target.value); setError(''); }} />
              <textarea className="input" placeholder="Research question (initial query)" value={queryInput} onChange={e => { setQueryInput(e.target.value); setError(''); }} rows={1} style={{ padding: '10px 16px', resize: 'vertical' }} />
              <button className="btn btn-primary" onClick={createSession} disabled={!projectId || !sessionTitle.trim() || loading}>
                {loading ? 'Creating...' : 'New Session'}
              </button>
            </div>
          )}
        </div>
        {error && <div className="error-banner" style={{ marginTop: 8 }}>{error} <button className="btn btn-secondary btn-sm" onClick={() => setError('')}>Dismiss</button></div>}
      </div>

      <div className="research-layout">
        <div className="research-sidebar">
          <h4>Sessions</h4>
          {sessions.length === 0 ? (
            <div className="empty-state-sm"><p>No sessions yet</p></div>
          ) : (
            <div className="session-list">
              {sessions.map(s => (
                <button key={s.session_id} className={`session-item ${activeSession?.session_id === s.session_id ? 'active' : ''}`}
                  onClick={() => loadSession(s)}>
                  <span className="session-title">{s.title}</span>
                  <span className={`session-status status-${s.status}`}>{s.status}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="research-main">
          <div className="research-tabs">
            <button className={`tab ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>Chat</button>
            <button className={`tab ${activeTab === 'sources' ? 'active' : ''}`} onClick={() => setActiveTab('sources')}>
              Sources {evidence.length > 0 && <span className="badge">{evidence.length}</span>}
            </button>
            <button className={`tab ${activeTab === 'report' ? 'active' : ''}`} onClick={() => setActiveTab('report')}>Report</button>
          </div>

          {activeTab === 'chat' && (
            <div className="chat-panel">
              {messages.length === 0 && !activeSession && (
                <div className="empty-state"><p>Select a project and create a new session above to begin.</p></div>
              )}
              {messages.length === 0 && activeSession && (
                <div className="empty-state"><p>Send a message to start the conversation</p></div>
              )}
              <div className="chat-messages">
                {messages.map((m, i) => (
                  <div key={i} className={`message message-${m.role}`}>
                    <div className="message-role">{m.role === 'user' ? 'You' : 'Atlas'}</div>
                    <div className="message-content">{m.content}</div>
                  </div>
                ))}
                {loading && <div className="message message-assistant"><div className="typing-indicator"><span /><span /><span /></div></div>}
                <div ref={chatEndRef} />
              </div>
              <div className="chat-input-area">
                <textarea className="chat-input" placeholder={activeSession ? "Ask a research question..." : "Create a session above to start chatting"} value={input}
                  onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  rows={2} disabled={loading || !activeSession} />
                <div className="chat-actions">
                  <button className="btn btn-primary" onClick={sendMessage} disabled={!input.trim() || loading || !activeSession}>Send</button>
                  <button className="btn btn-secondary" onClick={runFullResearch} disabled={!activeSession || loading}>
                    {loading ? 'Researching...' : 'Run Research'}
                  </button>
                  <button className="btn btn-secondary" onClick={doGenerateReport} disabled={!activeSession || loading}>
                    Generate Report
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'sources' && (
            <div className="sources-panel">
              {evidence.length === 0 ? (
                <div className="empty-state"><p>No sources collected yet. Run research to gather evidence.</p></div>
              ) : (
                evidence.map((e, i) => (
                  <div key={i} className="evidence-card">
                    <div className="evidence-header">
                      <span className="evidence-type">{e.evidence_type}</span>
                      <span className="evidence-confidence">{(e.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                    <h4 className="evidence-title">{e.title}</h4>
                    <p className="evidence-content">{e.content}</p>
                    {e.source_url && <a className="evidence-source" href={e.source_url} target="_blank" rel="noopener">{e.source_url}</a>}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'report' && (
            <div className="report-panel">
              {!report ? (
                <div className="empty-state">
                  <p>No report generated yet. Click "Generate Report" to create one.</p>
                  <button className="btn btn-primary" onClick={doGenerateReport} disabled={loading}>Generate Report</button>
                </div>
              ) : (
                <div className="report-content">
                  <h2>{report.title}</h2>
                  <section className="report-section">
                    <h3>Executive Summary</h3>
                    <p>{report.executive_summary}</p>
                  </section>
                  {report.sections?.map((s: any, i: number) => (
                    <section key={i} className="report-section">
                      <h3>{s.heading}</h3>
                      <p>{s.content}</p>
                    </section>
                  ))}
                  {report.citations?.length > 0 && (
                    <section className="report-section">
                      <h3>Citations</h3>
                      <ol className="citation-list">
                        {report.citations.map((c: any, i: number) => (
                          <li key={i}>{c.text} — <cite>{c.source}</cite></li>
                        ))}
                      </ol>
                    </section>
                  )}
                  {activeSession && (
                    <div className="export-actions">
                      <a className="btn btn-secondary" href={api.exportMarkdown(activeSession.session_id)} target="_blank" rel="noopener">
                        Export Markdown
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// --------------- Projects Page ---------------
function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState<Record<string, any[]>>({});

  const load = async () => {
    try {
      const d = await api.listProjects();
      setProjects(d.projects || []);
    } catch {}
  };

  useEffect(() => { load(); }, []);

  const create = async () => {
    if (!newName.trim()) return;
    setLoading(true);
    try {
      await api.createProject(newName, newDesc);
      setNewName('');
      setNewDesc('');
      await load();
    } catch (err: any) { alert('Failed: ' + err.message); }
    finally { setLoading(false); }
  };

  const del = async (id: string) => {
    try { await api.deleteProject(id); await load(); }
    catch (err: any) { alert('Failed: ' + err.message); }
  };

  const loadSessions = async (projectId: string) => {
    if (sessions[projectId]) return;
    try {
      const d = await api.listResearchSessions(projectId);
      setSessions(prev => ({ ...prev, [projectId]: d.sessions || [] }));
    } catch {}
  };

  return (
    <div className="page projects-page">
      <div className="page-header">
        <h2>Projects</h2>
        <div className="create-form">
          <input className="input" placeholder="Project name" value={newName} onChange={e => setNewName(e.target.value)} />
          <input className="input" placeholder="Description (optional)" value={newDesc} onChange={e => setNewDesc(e.target.value)} />
          <button className="btn btn-primary" onClick={create} disabled={!newName.trim() || loading}>Create</button>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state"><p>No projects yet. Create your first project above.</p></div>
      ) : (
        <div className="projects-grid">
          {projects.map(p => (
            <div key={p.project_id} className="project-card" onClick={() => loadSessions(p.project_id)}>
              <div className="project-card-header">
                <h3>{p.name}</h3>
                <button className="btn-icon" onClick={e => { e.stopPropagation(); del(p.project_id); }} aria-label="Delete">✕</button>
              </div>
              {p.description && <p className="project-desc">{p.description}</p>}
              <span className="project-date">{new Date(p.created_at).toLocaleDateString()}</span>
              {sessions[p.project_id] && (
                <div className="session-mini-list">
                  {sessions[p.project_id].slice(0, 3).map((s: any) => (
                    <span key={s.session_id} className="session-mini">{s.title}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// --------------- Library Page ---------------
function LibraryPage() {
  const [projectId, setProjectId] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<any>(null);
  const [chunks, setChunks] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.listProjects().then(d => setProjects(d.projects || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (projectId) {
      api.listDocuments(projectId).then(d => setDocuments(d.documents || [])).catch(() => {});
    }
  }, [projectId]);

  const viewDoc = async (doc: any) => {
    setSelectedDoc(doc);
    try {
      const d = await api.getDocumentChunks(doc.document_id);
      setChunks(d.chunks || []);
    } catch {}
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || !projectId) return;
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await api.uploadDocument(projectId, file);
      }
      const d = await api.listDocuments(projectId);
      setDocuments(d.documents || []);
    } catch (err: any) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="page library-page">
      <div className="page-header">
        <h2>Library</h2>
        <div className="library-controls">
          <select className="select-input" value={projectId} onChange={e => setProjectId(e.target.value)}>
            <option value="">Select project...</option>
            {projects.map(p => <option key={p.project_id} value={p.project_id}>{p.name}</option>)}
          </select>
          {projectId && (
            <>
              <input ref={fileInputRef} type="file" multiple accept=".pdf,.docx,.md,.txt" className="hidden-input"
                onChange={handleUpload} />
              <button className="btn btn-primary" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
                {uploading ? 'Uploading...' : 'Upload Files'}
              </button>
            </>
          )}
        </div>
      </div>

      <div className="library-layout">
        <div className="library-list">
          {!projectId ? (
            <div className="empty-state"><p>Select a project to view documents</p></div>
          ) : documents.length === 0 ? (
            <div className="empty-state"><p>No documents uploaded to this project</p></div>
          ) : (
            documents.map(d => (
              <div key={d.document_id} className={`doc-card ${selectedDoc?.document_id === d.document_id ? 'active' : ''}`}
                onClick={() => viewDoc(d)}>
                <h4>{d.title}</h4>
                <p className="doc-meta">{d.file_format.toUpperCase()} • {(d.file_size_bytes / 1024).toFixed(1)} KB</p>
              </div>
            ))
          )}
        </div>

        <div className="library-viewer">
          {!selectedDoc ? (
            <div className="empty-state"><p>Select a document to view its contents</p></div>
          ) : (
            <div className="doc-viewer">
              <h3>{selectedDoc.title}</h3>
              <p className="doc-meta">{selectedDoc.file_format.toUpperCase()} • {(selectedDoc.file_size_bytes / 1024).toFixed(1)} KB</p>
              <div className="chunks-list">
                {chunks.length === 0 ? (
                  <p>No text chunks extracted from this document.</p>
                ) : (
                  chunks.map((c, i) => (
                    <div key={i} className="chunk-card">
                      <span className="chunk-num">#{i + 1}</span>
                      <p>{c.content}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// --------------- Reports Page ---------------
function ReportsPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [projectId, setProjectId] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedReport, setSelectedReport] = useState<any>(null);

  useEffect(() => {
    api.listProjects().then(d => setProjects(d.projects || [])).catch(() => {});
  }, []);

  const loadSessions = async (pid: string) => {
    setProjectId(pid);
    try {
      const d = await api.listResearchSessions(pid);
      const reports = [];
      for (const s of (d.sessions || [])) {
        try {
          const r = await api.getReport(s.session_id);
          reports.push({ ...s, report: r });
        } catch {}
      }
      setSessions(reports);
    } catch {}
  };

  return (
    <div className="page reports-page">
      <div className="page-header">
        <h2>Reports</h2>
        <select className="select-input" value={projectId} onChange={e => loadSessions(e.target.value)}>
          <option value="">Select project...</option>
          {projects.map(p => <option key={p.project_id} value={p.project_id}>{p.name}</option>)}
        </select>
      </div>

      {!projectId ? (
        <div className="empty-state"><p>Select a project to view reports</p></div>
      ) : sessions.length === 0 ? (
        <div className="empty-state"><p>No reports generated yet. Run research and generate reports from the Research workspace.</p></div>
      ) : (
        <div className="reports-layout">
          <div className="reports-list">
            {sessions.map(s => (
              <div key={s.session_id} className={`report-card ${selectedReport?.session_id === s.session_id ? 'active' : ''}`}
                onClick={() => setSelectedReport(s)}>
                <h4>{s.title}</h4>
                <span className={`status-badge status-${s.status}`}>{s.status}</span>
              </div>
            ))}
          </div>
          <div className="report-detail">
            {!selectedReport ? (
              <div className="empty-state"><p>Select a report to view</p></div>
            ) : (
              <div className="report-content">
                <h2>{selectedReport.report?.title || selectedReport.title}</h2>
                {selectedReport.report?.executive_summary && (
                  <section><h3>Executive Summary</h3><p>{selectedReport.report.executive_summary}</p></section>
                )}
                {selectedReport.report?.sections?.map((s: any, i: number) => (
                  <section key={i}><h3>{s.heading}</h3><p>{s.content}</p></section>
                ))}
                {selectedReport.report?.citations?.length > 0 && (
                  <section><h3>Citations</h3>
                    <ol>{selectedReport.report.citations.map((c: any, i: number) => (
                      <li key={i}>{c.text} — <cite>{c.source}</cite></li>
                    ))}</ol>
                  </section>
                )}
                <div className="export-actions">
                  <a className="btn btn-secondary" href={api.exportMarkdown(selectedReport.session_id)} target="_blank" rel="noopener">
                    Export Markdown
                  </a>
                  <a className="btn btn-secondary" href={api.exportJson(selectedReport.session_id)} target="_blank" rel="noopener">
                    Export JSON
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// --------------- Settings Page ---------------
function SettingsPage() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (document.documentElement.dataset.theme as any) || 'dark');

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.dataset.theme = next;
  };

  const settings = [
    { label: 'Models', desc: 'Configure AI models and providers', comingSoon: true },
    { label: 'Research', desc: 'Research workflow defaults', comingSoon: true },
    { label: 'Privacy', desc: 'Data privacy and storage', comingSoon: true },
    { label: 'Cloud', desc: 'Cloud sync settings', comingSoon: true },
    { label: 'Local AI', desc: 'Local model configuration', comingSoon: true },
    { label: 'Appearance', desc: 'Theme and display', action: toggleTheme, activeLabel: `Theme: ${theme}` },
    { label: 'Keyboard', desc: 'Keyboard shortcuts', comingSoon: true },
    { label: 'About', desc: 'Version and credits', comingSoon: true },
  ];

  return (
    <div className="page settings-page">
      <div className="page-header">
        <h2>Settings</h2>
      </div>
      <div className="settings-grid">
        {settings.map(s => (
          <div key={s.label} className={`settings-card${s.comingSoon ? ' settings-card-disabled' : ''}`} onClick={s.action}>
            <h3>{s.label}</h3>
            <p>{s.desc}</p>
            {s.comingSoon && <span className="settings-coming-soon">Coming Soon</span>}
            {s.activeLabel && <span className="settings-value">{s.activeLabel}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

// --------------- App Shell ---------------
function AppShell() {
  const [active, setActive] = useState<Section>('chat');
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (document.documentElement.dataset.theme as any) || 'dark');
  const [backend, setBackend] = useState<BackendHealth>({ status: 'checking' });
  const [showWelcome, setShowWelcome] = useState(false);
  const { user, logout } = useAuth();

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.dataset.theme = next;
  };

  useEffect(() => {
    const check = async () => {
      try {
        const data = await api.health();
        setBackend({ status: 'ok', version: data.version, environment: (data as any).environment });
        if (data.first_run) setShowWelcome(true);
      } catch {
        setBackend({ status: 'offline' });
      }
    };
    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const seen = localStorage.getItem('atlas-welcome-seen');
    if (!seen) setShowWelcome(true);
  }, []);

  const dismissWelcome = () => {
    localStorage.setItem('atlas-welcome-seen', 'true');
    setShowWelcome(false);
  };

  const renderPage = () => {
    switch (active) {
      case 'chat': return <ChatView />;
      case 'research': return <ResearchPage />;
      case 'projects': return <ProjectsPage />;
      case 'library': return <LibraryPage />;
      case 'reports': return <ReportsPage />;
      case 'settings': return <SettingsPage />;
      default: return <ChatView />;
    }
  };

  return (
    <div className="app-shell">
      {showWelcome && <WelcomeOverlay onDismiss={dismissWelcome} />}
      <Sidebar active={active} onNavigate={setActive} theme={theme} onToggleTheme={toggleTheme} backend={backend} user={user} onLogout={logout} />
      <main className="main-content" aria-live="polite">
        {renderPage()}
      </main>
    </div>
  );
}

// --------------- Welcome Overlay ---------------
function WelcomeOverlay({ onDismiss }: { onDismiss: () => void }) {
  return (
    <div className="welcome-overlay">
      <div className="welcome-modal">
        <div className="welcome-icon">Atlas</div>
        <h1 className="welcome-title">Welcome to Atlas</h1>
        <p className="welcome-subtitle">Your local-first AI research workspace</p>
        <div className="welcome-steps">
          <div className="welcome-step">
            <span className="step-num">1</span>
            <div><strong>Ask Anything</strong><p>Just type your question — projects and workspaces are created automatically</p></div>
          </div>
          <div className="welcome-step">
            <span className="step-num">2</span>
            <div><strong>Explore Results</strong><p>Review AI responses, dive deeper, and manage conversations</p></div>
          </div>
          <div className="welcome-step">
            <span className="step-num">3</span>
            <div><strong>Go Further</strong><p>Use Projects, Reports, and Research for advanced workflows</p></div>
          </div>
        </div>
        <button className="btn btn-primary welcome-btn" onClick={onDismiss}>Get Started</button>
      </div>
    </div>
  );
}

// --------------- Not Found ---------------
function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <div className="auth-page">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        <h1 className="auth-logo">404</h1>
        <p className="auth-subtitle">Page not found</p>
        <button className="btn btn-primary btn-block" onClick={() => navigate('/')}>Go Home</button>
      </div>
    </div>
  );
}

// --------------- Root App ---------------
export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/*" element={<AppShell />} />
      </Routes>
    </AuthProvider>
  );
}

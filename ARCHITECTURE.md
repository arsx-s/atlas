# Architecture

## System Overview

```
Browser → Nginx → /api/* → Backend (FastAPI)
              → /*    → Static Files (React SPA)
```

## Backend

```
atlas_backend/
├── api/v1/          # REST routes (9 routers, 37 endpoints)
│   ├── auth.py      # Registration, login, token refresh
│   ├── projects.py  # Project CRUD + notes + timeline
│   ├── documents.py # Document ingest, parsing, chunking
│   ├── research_sessions.py  # Chat, streaming, evidence, reports
│   ├── search.py    # Multi-provider search
│   ├── export.py    # Markdown, JSON, PDF, DOCX export
│   ├── monitoring.py # Health check endpoints
│   ├── health.py    # Liveness & readiness
│   ├── local.py     # Local runtime info
│   └── sync.py      # Offline sync queue
├── auth/            # PBKDF2 + custom JWT
├── ai/              # LLM/Embedding providers (OpenAI, Anthropic, Google, DeepSeek, Ollama)
├── search/          # Search providers (Brave, Tavily, Crossref, etc.)
├── documents/       # Parsing (PDF, DOCX, MD, TXT), chunking, OCR
├── persistence/     # SQLite storage layer
├── orchestration/   # Research sessions, evidence tracking, report generation
├── data/            # PostgreSQL, Redis, Qdrant, Neo4j adapters
└── core/            # Config, errors, security, health reports
```

## Frontend

```
apps/web/
├── src/
│   ├── main.tsx     # React entry point with BrowserRouter
│   ├── App.tsx      # All page components + auth context
│   ├── api.ts       # REST API client
│   └── styles.css   # Design system (light/dark themes)
├── index.html
├── nginx.conf       # SPA fallback + API proxy config
├── vite.config.ts
└── package.json
```

## Data Flow

1. User uploads document → POST /api/v1/projects/{id}/documents/ingest
2. Backend parses file (pdfplumber/python-docx/markdown) → chunks text
3. Chunks stored in SQLite → available for search/analysis
4. User asks question → POST /api/v1/research-sessions/{id}/chat
5. Backend queries AI provider → returns cited answer
6. User runs research → backend searches web + academic sources
7. Evidence collected → stored in research_evidence table
8. User generates report → Markdown with citations + sections

## API Routes

See `backend/src/atlas_backend/api/v1/` for route definitions.

All routes are prefixed with `/api/v1`.

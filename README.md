# Atlas

Open-source research workspace. Upload documents, ask questions, get cited answers, and generate reports.

## Features

- **Multi-provider AI** — OpenAI, Anthropic, Google, DeepSeek, Ollama
- **Document processing** — PDF, DOCX, Markdown, TXT with semantic chunking
- **Web & academic search** — Brave, Tavily, arXiv, PubMed, Semantic Scholar, CrossRef
- **Research sessions** — Chat with context, collect evidence, generate structured reports
- **Export formats** — Markdown, JSON, PDF, DOCX
- **Local-first** — Works offline with SQLite and Ollama
- **Docker deploy** — Single command to production
- **Auth** — Email/password registration with JWT sessions
- **Streaming** — SSE-based real-time AI responses

## Architecture

```
Browser → Nginx → /api/* → FastAPI (Python)
              → /*    → Static SPA (React)
```

**Backend** — FastAPI with SQLite/PostgreSQL, REST + SSE, pluggable AI/search providers
**Frontend** — React 18, TypeScript, Vite, react-router-dom

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Uvicorn |
| Frontend | React 18, TypeScript, Vite |
| Database | SQLite (default), PostgreSQL (optional) |
| Vector Store | Qdrant (optional) |
| Graph | Neo4j (optional) |
| Cache | Redis (optional) |
| Storage | Filesystem, S3-compatible |
| AI | OpenAI, Anthropic, Google, DeepSeek, Ollama |
| Search | Brave, Tavily, arXiv, PubMed, Semantic Scholar, CrossRef, DuckDuckGo |
| Infrastructure | Docker, Docker Compose |

## Quick Start

```bash
cp .env.example .env
# Set ATLAS_JWT_SECRET and at least one AI provider API key in .env
docker compose up
```

Open http://localhost

## Development

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn atlas_backend.main:app --reload --port 8000

# Frontend
cd apps/web
npm install
npm run dev
```

Frontend at http://localhost:5173, backend at http://localhost:8000.

## Docker

```bash
# Development (with hot reload)
docker compose up

# Production
cp .env.prod.example .env.prod
docker compose -f docker-compose.prod.yml up -d
```

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for platform-specific guides (Railway, Render, Fly.io, Vercel).

## Roadmap

- [x] Core research pipeline (chat, evidence, reports)
- [x] Multi-provider AI and search abstraction
- [x] Document ingestion (PDF, DOCX, MD, TXT)
- [x] Export (Markdown, JSON, PDF, DOCX)
- [x] Auth system (register, login, JWT)
- [x] Docker deployment
- [ ] Knowledge graph visualization
- [ ] Collaborative sessions
- [ ] Plugin system
- [ ] Mobile clients

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT

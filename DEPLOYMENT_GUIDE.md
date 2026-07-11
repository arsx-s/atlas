# Deployment Guide

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) v2+
- Git
- API keys for at least one AI provider (see below)

## Quick Start (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/atlas.git
cd atlas

# 2. Copy environment file
cp .env.example .env

# 3. Set a JWT secret (required)
#    Generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
#    Then edit .env and set ATLAS_JWT_SECRET=<your-secret>

# 4. Launch with Docker Compose
docker compose up
```

Open **http://localhost** in your browser.

---

## Step-by-Step Deployment

### Step 1: Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

**Required settings in `.env`:**

| Variable | Description | Example |
|---|---|---|
| `ATLAS_JWT_SECRET` | Secret for JWT tokens (generate with Python) | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` or `GOOGLE_API_KEY` | At least one AI provider | `sk-proj-...` |

**Optional but recommended:**

| Variable | Description |
|---|---|
| `TAVILY_API_KEY` | Web search provider |
| `BRAVE_API_KEY` | Alternative web search provider |
| `ATLAS_LOG_LEVEL` | `debug`, `info`, `warning`, `error` |

### Step 2: Choose a Deployment Mode

#### A. Development (with hot-reload)

```bash
docker compose up
```

- Backend at `http://localhost:8000`
- Frontend at `http://localhost:80`
- API docs at `http://localhost:8000/api/v1/docs`
- Live code reload via volume mounts

#### B. Production

```bash
cp .env.prod.example .env.prod
# Edit .env.prod with production secrets
docker compose -f docker-compose.prod.yml up -d
```

- Optimized containers (no dev dependencies)
- Restart policy: `unless-stopped`
- Health check on backend
- Persistent volume for SQLite, documents, and storage

### Step 3: Configure AI Providers

Atlas needs at least one AI provider for research features. Set the corresponding environment variable:

**OpenAI** (recommended)
```
OPENAI_API_KEY=sk-proj-your-key-here
```

**Anthropic**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Google Gemini**
```
GOOGLE_API_KEY=AIzaSy-your-key-here
```

### Step 4: Verify the Deployment

After containers start, verify:

```bash
# Check container status
docker compose ps

# Check backend health
curl http://localhost:8000/api/v1/health

# Check monitoring endpoints
curl http://localhost:8000/api/v1/monitoring/ping
curl http://localhost:8000/api/v1/monitoring/healthz

# Open in browser
open http://localhost
```

Expected health response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "0.1.0",
    "environment": "development",
    "first_run": true
  }
}
```

---

## Production Deployment

### Platform-Specific Guides

#### Railway

1. Push to GitHub
2. Create a new Railway project from your repo
3. Add a web service:
   - **Root directory:** `backend`
   - **Start command:** `uvicorn atlas_backend.main:app --host 0.0.0.0 --port $PORT`
4. Add a static site:
   - **Root directory:** `apps/web`
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
5. Set environment variables from `.env.prod`

#### Render

1. **Web Service** — Backend
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn atlas_backend.main:app --host 0.0.0.0 --port $PORT`

2. **Static Site** — Frontend
   - Build command: `npm run build`
   - Publish directory: `dist`

#### Fly.io

```bash
fly launch --no-deploy
fly secrets set ATLAS_JWT_SECRET=<secret> OPENAI_API_KEY=<key>
fly deploy
```

#### Vercel (frontend only)

```bash
cd apps/web
npm install
npx vercel --prod
```

Configure `VITE_ATLAS_API_BASE_URL` to point to your backend URL.

### Environment Variables for Production

All variables are documented in `.env.prod.example`. Key ones:

| Variable | Production Value |
|---|---|
| `ATLAS_ENV` | `production` |
| `ATLAS_HTTPS_ONLY` | `true` |
| `ATLAS_LOG_LEVEL` | `info` |
| `ATLAS_CORS_ALLOWED_ORIGINS` | Your frontend domain(s) |
| `ATLAS_RATE_LIMIT_ENABLED` | `true` |
| `ATLAS_JWT_SECRET` | Secure random value |

### Data Persistence

In production Docker mode, data is stored in a Docker volume named `atlas-data`:

- `/data/atlas-local.db` — SQLite database
- `/data/documents/` — Uploaded documents
- `/data/storage/` — File storage

To back up:

```bash
docker run --rm -v atlas-data:/data -v $(pwd):/backup alpine tar czf /backup/atlas-backup-$(date +%Y%m%d).tar.gz -C /data .
```

---

## Manual Deployment (without Docker)

### Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn atlas_backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd apps/web
npm install
npm run dev        # Development
npm run build      # Production (output in dist/)
```

For production, serve the `dist/` directory with any HTTP server (nginx, caddy, etc.).

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `Connection refused` on startup | Backend takes ~5s to initialize; wait and retry |
| `JWT secret not configured` | Set `ATLAS_JWT_SECRET` in `.env` |
| `No AI provider configured` | Set at least `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` |
| Frontend shows blank page | Check browser console; ensure `VITE_ATLAS_API_BASE_URL` is set correctly |
| Docker volume permission errors | Run `chmod -R 777 /data` inside container or set `user` in compose |
| Port 80 already in use | Change frontend port in `docker-compose.yml` |

## Security Checklist

- [ ] `ATLAS_JWT_SECRET` is set to a unique, random value
- [ ] `ATLAS_HTTPS_ONLY=true` in production
- [ ] `ATLAS_CORS_ALLOWED_ORIGINS` is restricted to your domain(s)
- [ ] `ATLAS_RATE_LIMIT_ENABLED=true`
- [ ] API keys are stored in environment variables, not in code
- [ ] `.env` and `.env.prod` are in `.gitignore`
- [ ] Docker containers run as non-root (handled by default)

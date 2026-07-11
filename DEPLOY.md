# Deployment Guide

This document describes how to deploy Atlas to production.

## Architecture

```
Browser → Vercel (Frontend: React SPA) → Render (Backend: FastAPI) → SQLite/PostgreSQL
                                                                   → OpenAI/Anthropic/etc.
                                                                   → Tavily/Brave/etc.
```

- **Frontend**: Deployed on Vercel as a static SPA
- **Backend**: Deployed on Render as a Python web service
- **Database**: SQLite (Render disk) or PostgreSQL (Render managed)
- **AI Providers**: OpenAI, Anthropic, Google — set via environment variables

---

## Option 1: Vercel (Frontend) + Render (Backend)

### Step 1: Deploy the Backend to Render

1. Push your repository to GitHub.
2. Log in to [Render](https://render.com) → **New** → **Web Service**.
3. Connect your GitHub repository.
4. Configure the web service:

   | Setting | Value |
   |---------|-------|
   | **Root Directory** | `backend` |
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn atlas_backend.main:app --host 0.0.0.0 --port $PORT --workers 2 --proxy-headers --forwarded-allow-ips "*"` |
   | **Health Check Path** | `/api/v1/health` |

5. Add a **Persistent Disk** (Render → your service → Disks):
   - Name: `atlas-data`
   - Mount Path: `/var/data`
   - Size: 1 GB (or more for production)

6. Set environment variables (see [Environment Variables](#environment-variables) section below).

7. Deploy. Note your backend URL (e.g. `https://atlas-backend.onrender.com`).

### Step 2: Deploy the Frontend to Vercel

1. In your Vercel dashboard, click **Add New** → **Project**.
2. Import your GitHub repository.
3. Configure the project:

   | Setting | Value |
   |---------|-------|
   | **Root Directory** | `apps/web` |
   | **Framework Preset** | Vite |
   | **Build Command** | `npm run build` (default) |
   | **Output Directory** | `dist` (default) |

4. Add environment variable:

   | Key | Value |
   |-----|-------|
   | `VITE_ATLAS_API_BASE_URL` | `https://your-backend.onrender.com/api/v1` |

5. Deploy. Your frontend will be live at a `*.vercel.app` URL.

6. **Important**: Go back to Render and update `ATLAS_CORS_ALLOWED_ORIGINS` to your Vercel frontend URL (e.g. `https://atlas-web.vercel.app`), then redeploy the backend.

---

## Option 2: Docker (Full Stack)

For single-server deployment:

```bash
cp .env.prod.example .env.prod
# Edit .env.prod with all secrets
docker compose -f docker-compose.prod.yml up -d
```

The Docker Compose setup bundles both frontend (nginx) and backend (uvicorn) in one deployment. Frontend is served on port 80; backend on port 8000.

### Updating

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Environment Variables

### Backend (Render / Docker)

#### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `ATLAS_JWT_SECRET` | JWT signing secret | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| *or* `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |
| *or* `GOOGLE_API_KEY` | Google/Gemini API key | `AIzaSy...` |

#### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `ATLAS_ENV` | `production` | Runtime environment |
| `ATLAS_RUNTIME_MODE` | `hybrid` | `local`, `cloud`, or `hybrid` |
| `ATLAS_API_BASE_PATH` | `/api/v1` | API route prefix |
| `ATLAS_LOG_LEVEL` | `info` | Log level: `debug`, `info`, `warning`, `error` |
| `ATLAS_HTTPS_ONLY` | `true` | Enforce HTTPS redirects |
| `ATLAS_CORS_ALLOWED_ORIGINS` | — | Comma-separated allowed origins (set to your frontend URL) |
| `ATLAS_RATE_LIMIT_ENABLED` | `true` | Enable rate limiting (100 req/hour/IP) |

#### Data

| Variable | Default | Description |
|----------|---------|-------------|
| `ATLAS_SQLITE_PATH` | `/var/data/atlas.db` | SQLite database path |
| `ATLAS_DOCUMENTS_PATH` | `/var/data/documents` | Uploaded document storage |
| `ATLAS_STORAGE_PATH` | `/var/data/storage` | File storage path |
| `DATABASE_URL` | — | PostgreSQL connection string (optional, replaces SQLite) |
| `REDIS_URL` | — | Redis connection string (optional) |
| `QDRANT_URL` | — | Qdrant connection string (optional) |
| `NEO4J_URL` | — | Neo4j connection string (optional) |

#### Optional Providers

| Variable | Description |
|----------|-------------|
| `DEEPSEEK_API_KEY` | DeepSeek LLM provider |
| `TAVILY_API_KEY` | Web search provider |
| `BRAVE_API_KEY` | Web search provider |
| `AWS_S3_BUCKET` | S3 bucket for file storage |
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |

### Frontend (Vercel)

| Variable | Description |
|----------|-------------|
| `VITE_ATLAS_API_BASE_URL` | Backend API base URL (e.g. `https://your-backend.onrender.com/api/v1`) |

---

## Custom Domains

### Vercel

1. Go to your Vercel project → **Settings** → **Domains**.
2. Add your domain (e.g. `app.yourdomain.com`).
3. Update DNS: add a CNAME record pointing to `cname.vercel-dns.com`.
4. Vercel provisions a TLS certificate automatically.

### Render

1. Go to your Render service → **Settings** → **Custom Domain**.
2. Add your domain (e.g. `api.yourdomain.com`).
3. Update DNS: add a CNAME record pointing to `onrender.com`.
4. Render provisions a TLS certificate automatically.

Update `ATLAS_CORS_ALLOWED_ORIGINS` to include your custom frontend domain.

---

## HTTPS

- **Vercel**: HTTPS is automatic for all `*.vercel.app` domains and custom domains.
- **Render**: HTTPS is automatic for all `*.onrender.com` domains and custom domains.
- **Docker**: Behind a reverse proxy (nginx/Caddy/Traefik) with Let's Encrypt.

Ensure `ATLAS_HTTPS_ONLY=true` in production.

---

## Production Checklist

- [ ] `ATLAS_JWT_SECRET` is set to a unique, random value (64+ chars)
- [ ] At least one AI provider API key is configured
- [ ] `ATLAS_CORS_ALLOWED_ORIGINS` is restricted to your frontend domain(s)
- [ ] `ATLAS_ENV=production`
- [ ] `ATLAS_HTTPS_ONLY=true`
- [ ] `ATLAS_RATE_LIMIT_ENABLED=true`
- [ ] Render persistent disk is configured for data storage
- [ ] Vercel `VITE_ATLAS_API_BASE_URL` points to the Render backend
- [ ] Backend health check passes: `GET /api/v1/health`
- [ ] Frontend API calls reach the backend (check browser DevTools Network tab)
- [ ] Registration and login work end-to-end
- [ ] Custom domain DNS has propagated (if using custom domains)
- [ ] Database backups are configured (Render automated backups or cron job for SQLite)

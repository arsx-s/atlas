# Atlas Web

Atlas Web shares the backend API, design system, and reusable packages with Desktop. In beta, Web provides the calm research workspace surface for home, research, projects, library, reports, documents, and settings.

## Current Scope

- Provide the research workspace shell for local or cloud-backed sessions.
- Poll backend health and use the search and research session APIs.
- Present a polished split-view research layout with documents, sources, and settings.
- Keep Web aligned with the backend API contracts and shared workspace packages.

## Launch

From the repository root:

```powershell
pnpm dev:web
```

Set `VITE_ATLAS_API_BASE_URL` if you want to target a backend on another host, or leave it unset to use the local proxy target.

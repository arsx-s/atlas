# Atlas Desktop

Atlas Desktop is the primary beta delivery surface because Local AI, offline mode, local file processing, local databases, and user-controlled privacy are core product differentiators.

## Current Scope

- Launch the Atlas backend automatically on startup.
- Expose a calm research workspace UI with dashboard, research, projects, documents, and settings.
- Support local file import, backend health checks, update checks, and deep-link aware startup.
- Keep Desktop aligned with the backend API contracts and shared workspace packages.

## Launch

From the repository root:

```powershell
pnpm dev:desktop
```

If the backend is not already running, Desktop will try to start it automatically with the configured Python runtime.

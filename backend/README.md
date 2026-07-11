# Atlas Backend

The backend will use Python and FastAPI. It owns versioned APIs, authentication, validation, orchestration entry points, persistence coordination, and integration with infrastructure services.

## Milestone 1 Scope

- Define backend package metadata.
- Document backend ownership boundaries.
- Avoid production API feature code until Milestone 2.

## Milestone 2 Scope

- Typed configuration contract.
- Standard API response envelopes.
- Atlas exception and error mapping.
- Health and readiness contracts.
- Local-device and cloud-user request principal boundaries.
- FastAPI app factory.
- Versioned v1 health and readiness routes.

## Required Backend Principles

- Every protected cloud endpoint requires authentication.
- Local mode uses local device identity instead of Atlas account authentication.
- All responses use the standard Atlas response envelope.
- API versions are explicit.
- Business logic stays outside UI code.

## Runtime Note

FastAPI is declared in `pyproject.toml`. The current Codex bundled runtime does not have FastAPI installed, so dependency-free backend contracts are verified by unit tests and the app factory reports missing runtime dependencies clearly until backend dependencies are installed.

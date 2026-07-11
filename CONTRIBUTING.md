# Contributing to Atlas

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install dependencies:
   ```bash
   cd backend && pip install -e ".[dev]"
   cd apps/web && npm install
   ```
4. Run tests:
   ```bash
   cd backend && pytest
   cd apps/web && npm run build
   ```

## Guidelines

- Keep changes focused — one PR per feature/fix
- Maintain existing code style (type hints, async patterns)
- Update `.env.example` when adding new environment variables
- Ensure frontend builds without warnings
- Ensure Docker Compose works with your changes
- Add tests for new backend routes

## Project Structure

```
backend/src/atlas_backend/   # Python FastAPI backend
apps/web/src/                # React TypeScript frontend
```

## Code Review

All submissions require review. Maintainers may ask for changes before merging.

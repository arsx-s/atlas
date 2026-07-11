# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x     | ✅ Yes             |

## Reporting a Vulnerability

Open an issue with the `security` label, or email the maintainers directly. Do not publicly disclose until resolved.

## Security Practices

- JWT tokens use HS256 with configurable secret
- Passwords hashed with PBKDF2 (100,000 iterations)
- CORS is configurable via environment variables
- No secrets are bundled in the codebase
- Docker images run as non-root user
- API keys are never logged

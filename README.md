# Marketing Analytics AI Agent

FastAPI-powered backend and Next.js frontend that converts marketing questions into ClickHouse SQL, executes the query, and returns a narrated insight. The backend now follows a layered architecture with explicit domain and infrastructure boundaries to support new LLM providers and future scale.

## Backend Overview

- **API layer**: `app/api` provides dependency wiring, error handling, health checks, and the `/api/v1/query` endpoint (rate limited with SlowAPI).
- **Domain layer**: `app/domain` owns DTOs, prompt rendering, SQL sanitation, conversation memory, and the main `QueryOrchestrator` use case.
- **Infrastructure layer**: `app/infra` contains adapters for ClickHouse, Redis caching, LLM clients, configuration, CORS, logging, and rate limits.
- **Orchestration**: `app/app.py` builds the FastAPI instance, wires middleware, structured logging with request ids, and bootstraps ClickHouse seed data on startup.

## Getting Started

1. **Prerequisites**
   - Docker + Docker Compose (for ClickHouse/Redis/back-end runtime)
   - Node.js 18+ (for the frontend)
   - Python 3.11 (for local tooling/tests)
2. **Environment configuration**
   ```bash
   cp .env.example .env
   # populate CLICKHOUSE_*, REDIS_URL, and LLM_API_KEY secrets
   ```
3. **Run the stack**
   ```bash
   docker compose up --build
   ```
   Services become available at:
   - Backend API: http://localhost:8000
   - ClickHouse native: localhost:9000 (HTTP: http://localhost:8123)
   - Redis: localhost:6379
4. **Seed ClickHouse**
   ```bash
   docker compose run --rm backend python -m app.infra.clickhouse.seed_data
   ```
5. **Frontend (optional)**
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```
   Configure `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` to point at the backend (required for production/static builds). See [frontend/README.md](frontend/README.md) for the full UI guide.

## Developer Tooling

All backend commands are wrapped in `backend/Makefile`:

```bash
cd backend
make dev       # uvicorn app.main:app --reload
make lint      # ruff + black --check + mypy
make format    # black + ruff --fix
make test      # pytest -q
make seed      # run ClickHouse seed script via Docker
```

Install dependencies locally with:

```bash
pip install -r backend/requirements.txt -r requirements-dev.txt
```

## Frontend Overview

The marketing copilot UI lives under [`frontend/`](frontend). Key points:

- **App Router + React 19** with clear separation between server (`app/page.tsx`) and client components (`app/components/agent/*`).
- **Shared primitives** live under `app/components/ui`, hooks under `app/lib/hooks`, and API access through `app/lib/api` with Zod validation.
- **State management** uses React Query via `ReactQueryProvider` and the `useAgentConsole` hook for rate limiting, caching, and optimistic updates.
- **Performance**: heavy widgets (data table) are lazy-loaded with `next/dynamic`, and a bundle analyzer (`pnpm analyze`) is available for profiling.
- **Tooling**: ESLint flat config (`eslint.config.mjs`), Vitest (`vitest.config.ts`), Tailwind CSS (`tailwind.config.ts`), and strict TypeScript (`tsconfig.json`).

Refer to [frontend/README.md](frontend/README.md) for scripts, environment configuration, and testing workflows.

## API Reference

- `POST /api/v1/query`
  ```json
  {
    "question": "Show ROAS and CTR by source for the last 7 days",
    "user_id": "user-123"
  }
  ```
  Response:
  ```json
  {
    "sql": "SELECT ...",
    "data": [{"source": "facebook", "spend": 10234.58}],
    "summary": "Facebook Ads delivered higher ROAS ..."
  }
  ```
- `GET /health` — lightweight liveness check.
- `GET /ready` — readiness probe that verifies ClickHouse and Redis connectivity.

## Repository Layout (Backend)

```
backend/
  app/
    api/
      deps.py          # FastAPI dependency providers
      errors.py        # HTTP exception mapping
      health.py        # /health and /ready endpoints
      routes/          # /query router + rate limiter
    app.py             # FastAPI factory with middleware and bootstrap
    domain/
      models/          # Pydantic DTOs
      prompts/         # Prompt templates stored on disk
      services/        # Orchestrator, memory, prompt builder, sql tools
    infra/
      cache/           # Redis adapter + key builders
      clickhouse/      # Async client, schema, bootstrap helpers
      config.py        # Pydantic settings + env validation
      cors.py, logging.py, rate_limit.py, llm/
    main.py            # ASGI entrypoint for uvicorn
  Makefile             # Developer commands
  pyproject.toml       # black/ruff/mypy/pytest config
  Dockerfile           # Backend container image
```

Tests live under `backend/tests/` with `unit/` (pure functions) and `integration/` smoke tests that override infrastructure with stubs.

## Testing

```bash
cd backend
make test
```

Key coverage:

- `backend/tests/unit/test_sql_normalizer.py` — safety checks for SQL normalization and validation.
- `backend/tests/unit/test_sql_builder.py` — LLM output normalisation.
- `backend/tests/unit/test_cache_keys.py` — deterministic cache hashing.
- `backend/tests/integration/test_query_endpoint.py` — `/query` happy path with stubbed LLM/ClickHouse/Redis.

## Operations Notes

- Structured logging with request IDs is configured in `infra/logging.py`.
- ClickHouse bootstrap and seeding are idempotent (`infra/clickhouse/bootstrap.py`).
- Redis caching uses deterministic keys derived from question + normalised SQL.
- `Settings` (`infra/config.py`) enforce required secrets per LLM provider and expose a sanitised dict for logging.

## Frontend

The Next.js application remains under `frontend/` and communicates with the backend via the `/api/v1/query` endpoint. See `frontend/README.md` (if present) or use the standard Next.js workflow (`npm install && npm run dev`).

## Contributing & Future Work

Planned enhancements are tracked in `FOLLOW-UPS.md`. Security posture (LLM output handling, SQL guardrails, secret management) is summarised in `SECURITY.md`. Contributions should maintain 100% typed code, follow `make lint`, and include appropriate tests.

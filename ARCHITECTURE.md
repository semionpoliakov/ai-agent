# Architecture

## Overview

The backend is organised around a clean architecture split into API, Domain, and Infrastructure layers. The goal is to allow new LLM providers or data stores without rewriting business logic while keeping FastAPI as a thin delivery mechanism.

```
┌──────────────┐    ┌────────────────┐    ┌──────────────────┐
│ HTTP Client  │ -> │ FastAPI Router │ -> │ QueryOrchestrator │
└──────────────┘    └────────────────┘    └────────┬─────────┘
                                                   │
                 ┌───────────────┐  ┌──────────────┴──────────────┐  ┌────────────────┐
                 │ Prompt Builder│  │ SQL Builder & Validator     │  │ Conversation    │
                 │ (Domain)      │  │ (Domain)                    │  │ Memory (Domain) │
                 └──────┬────────┘  └──────────────┬──────────────┘  └────────┬───────┘
                        │                          │                           │
             ┌──────────▼────────┐        ┌────────▼────────┐        ┌────────▼────────┐
             │ LLM Client (Infra)│        │ ClickHouse Client│        │ Redis Cache     │
             └───────────────────┘        └──────────────────┘        └────────────────┘
```

## Layer Responsibilities

- **API (`app/api`)**: request validation, dependency injection, error mapping, and rate limiting. Routers remain slim and delegate to domain services.
- **Domain (`app/domain`)**: prompt rendering, orchestration logic, SQL hygiene, DTOs, and ephemeral conversation memory.
- **Infrastructure (`app/infra`)**: adapters for ClickHouse, Redis caching, LLM providers, typed configuration, logging, CORS, and rate limits.

`QueryOrchestrator` sits in the domain layer and coordinates the following workflow:

1. Check Redis for cached question/SQL fingerprint.
2. Render the SQL prompt (history-aware) and invoke the configured LLM client.
3. Normalise and validate the SQL before executing the ClickHouse query.
4. Generate the summary prompt, invoke the LLM again, and store both SQL + summary in cache and memory.

## Key Modules

- `app/app.py`: FastAPI factory configuring middleware, request ID logging, CORS, exception handlers, and startup bootstrap.
- `app/domain/services/sql_builder.py`: Strips think tags/code fences, collapses whitespace, and prepares SQL for validation.
- `app/domain/services/sql_validator.py`: Guards against multi-statements, comments, and mutation keywords.
- `app/infra/llm`: Protocol + Groq implementation. A factory selects providers via environment variables.
- `app/infra/clickhouse`: Async client wrapping `clickhouse-driver` plus schema bootstrap + deterministic seed data.
- `app/infra/cache`: Redis asyncio adapter with JSON helpers and key builders.

## Extensibility

- **New LLM providers**: implement `LLMClientProtocol` in `app/infra/llm` and register within `factory.py`.
- **Alternative storage**: create new adapters under `app/infra`, expose FastAPI dependencies in `api/deps.py`, and adjust orchestrator wiring.
- **Prompt variations**: edit `app/domain/prompts/*.txt` templates or add new ones; `prompt_builder.py` handles placeholder substitution.

## Observability & Operations

- Structured logging with per-request IDs (`infra/logging.py`).
- `/health` (liveness) and `/ready` (readiness) endpoints for Kubernetes probes.
- Rate limiting via SlowAPI (`infra/rate_limit.py`), configured by `RATE_LIMIT_PER_MINUTE`.
- Configuration validated centrally in `infra/config.py`, preventing boot when secrets are missing.

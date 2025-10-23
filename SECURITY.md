# Security Posture

## LLM Output Handling

- Raw completions are normalised via `sql_builder.clean_sql_output()` which strips `<think>` tags, code fences, `SQL:` labels, and trailing semicolons before validation.
- `normalize_sql_for_clickhouse()` (`app/infra/sql/normalizer.py`) converts generic SQL to ClickHouse syntax and applies `validate_clickhouse_sql()` to reject DDL/DML, multi-statements, comments, and unsafe keywords.
- Summaries are also stripped of `<think>` tags to avoid leaking chain-of-thought content back to end users.

## Data Access Controls

- ClickHouse queries are executed via an async adapter that only exposes read methods (`query` + `execute_scalar`).
- Bootstrap scripts are idempotent and log the dataset status for audit visibility.
- Redis cache keys use SHA-256 fingerprints of question + normalised SQL; stored payloads are JSON encoded and respect TTL from configuration.

## Configuration & Secrets

- Environment variables are validated through `app/infra/config.py`. Each provider must supply `LLM_API_KEY`; boot fails fast if secrets are missing or provider is unsupported.
- Logs emit only sanitised configuration, never raw secrets.

## Transport & API Safety

- Rate limiting enforced by SlowAPI on `/api/v1/query` with configurable requests-per-minute (default 30).
- CORS restricted to a single allowed origin when `CORS_ALLOWED_ORIGIN` is set.
- `/ready` and `/health` endpoints expose minimal operational data suitable for load balancer probes.

## Follow-up Opportunities

- Implement structured audit logs for ClickHouse queries (question hash, execution time, rows returned).
- Add request-level authentication / API tokens for multi-tenant deployments.
- Integrate content filtering / prompt injection detection before invoking the LLM.
- Gate expensive operations with circuit breakers backed by Redis counters.

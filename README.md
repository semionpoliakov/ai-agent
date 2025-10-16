# Marketing Analytics AI Agent

Full-stack AI assistant that translates natural-language marketing questions into ClickHouse SQL, executes queries, and returns narrative insights via a Next.js chat UI. Designed for Vercel (frontend) and Render/Railway (backend + ClickHouse + Redis) deployments.

## Architecture
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind + shadcn-inspired UI + React Query client-side caching.
- **Backend**: FastAPI (async) orchestrating Gemini Flash for SQL + summary, async ClickHouse driver, Redis cache, SlowAPI rate limiting, in-memory chat context.
- **Data**: ClickHouse with synthetic ad performance data, seedable via Faker, backed by Redis caching. All containerised with Docker Compose.

## Getting Started
1. **Prerequisites**: Docker, Docker Compose, Node.js 18+, Python 3.11+ (optional for local tooling).
2. **Environment**:
   ```bash
   cp .env.example .env
   # edit GEMINI_API_KEY and other secrets as needed
   ```
3. **Boot services**:
   ```bash
   docker compose up --build
   ```
   - FastAPI backend: `http://localhost:8000`
   - ClickHouse native: `localhost:9000`, HTTP: `http://localhost:8123`
   - Redis: `localhost:6379`
4. **Seed data** (after containers are healthy):
   ```bash
   docker compose run --rm backend python /app/db/seed_data.py
   ```
5. **Run frontend locally**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Configure `NEXT_PUBLIC_API_BASE_URL` (e.g. in `.env.local`) to point to the backend when deploying to Vercel.

## Deployment Notes
- **Frontend**: Push `frontend` directory to Vercel; set environment variable `NEXT_PUBLIC_API_BASE_URL` to your backend URL.
- **Backend**: Deploy the `backend` service (with `backend/Dockerfile`) to Render or Railway, attach environment variables from `.env`, and provision ClickHouse + Redis services using managed offerings or the provided Compose setup.

## API Reference
`POST /api/v1/query`
```json
{
  "question": "Show ROAS and CTR by source for the last 7 days",
  "user_id": "user-123"
}
```
Response
```json
{
  "sql": "SELECT ...",
  "data": [
    {"source": "facebook_ads", "spend": 10234.58, "clicks": 3845, "ctr": 0.12, "roas": 2.45},
    {"source": "google_ads", "spend": 8421.77, "clicks": 3104, "ctr": 0.11, "roas": 2.11}
  ],
  "summary": "Facebook Ads delivered higher ROAS ..."
}
```
`GET /health` returns ClickHouse/Redis health flags.

## Project Structure
```
backend/
  app/
    api/          # FastAPI routers + rate limiting
    core/         # Settings, cache, memory
    models/       # Pydantic schemas
    services/     # ClickHouse, LLM client, SQL validator
  llm_orchestrator.py  # Multi-step agent pipeline
  Dockerfile
frontend/
  app/           # Next.js App Router pages, error boundary
  components/    # shadcn-style UI primitives, data table
  lib/           # React Query provider, rate limiter, API client
  package.json
  tailwind.config.ts
  next.config.js
db/
  init.sql       # Schema bootstrap
  seed_data.py   # Faker-powered dataset (>1000 rows)
tests/
  test_sql_validator.py
```

## Example Question & Result
- **Question**: “What are the spend quantiles and unique campaigns in the US over the last 90 days?”
- **Generated SQL**: Uses `quantiles(0.25, 0.5, 0.75)(spend)` and `uniqExact(campaign_id)` over ClickHouse data.
- **Summary**: Explains spend distribution, CTR/ROAS highlights, and campaign diversity.
- **UI Output**: Summary paragraph plus table columns `source`, `spend`, `clicks`, `ctr`, `roas`, available for CSV download and SQL preview.

### Sample Data Snapshot
| date       | source        | spend  | clicks | ctr  | roas |
|------------|---------------|--------|--------|------|------|
| 2024-02-12 | facebook_ads  | 1245.3 | 532    | 0.12 | 2.18 |
| 2024-02-12 | google_ads    | 980.6  | 421    | 0.11 | 1.94 |

## Testing
```bash
pip install -r backend/requirements.txt -r requirements-dev.txt
pytest
```
`test_sql_validator.py` validates SQL filtering logic without external dependencies.

## TODO / Future Enhancements
- Observability stack (Prometheus, Grafana, OpenTelemetry).
- CI/CD pipeline (GitHub Actions) for automated testing and deploys.
- Horizontal scaling via Kubernetes + Helm charts.
- Multi-model LLM orchestration for SQL + narrative ensembles.
- Multi-tenant chat sessions with persistent storage.
- ClickHouse materialized views for high-frequency aggregations.
- Fine-tuning and persona-driven agent responses.
- Edge runtime support with streaming answer delivery.
- Frontend rate limiting backed by shared state and prompt-injection content scanning.

# Follow-ups

1. **LLM provider abstraction**
   - Implement additional provider adapters (OpenAI, Vertex) behind `app/infra/llm/factory.py` once credentials are available.
   - Expand configuration validation with provider-specific options (base URLs, organisation ids).
2. **Observability**
   - Introduce Prometheus metrics (latency histograms, cache hit rate, ClickHouse query durations).
   - Wire structured logs into a central sink (ELK/OTEL) and add correlation ids for LLM + ClickHouse calls.
3. **Testing depth**
   - Add property-based fuzzing for `sql_validator` covering quoted identifiers and nested functions.
   - Provide contract tests for Redis cache behaviour under concurrent access.
4. **Security enhancements**
   - Enforce API authentication (JWT or signed headers) before /query.
   - Add configurable allowlists for ClickHouse functions exposed to the LLM prompt.
5. **Performance**
   - Pool ClickHouse connections and measure async executor utilisation.
   - Cache prompt templates in memory to avoid disk reads on each request.
6. **Frontend alignment**
   - Update Next.js client to surface request ids, show /ready status, and handle degraded responses gracefully.

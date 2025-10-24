# Marketing Analytics AI Agent

FastAPI backend and Next.js frontend that convert marketing questions into ClickHouse SQL, execute the query, and return summarized insights.

## Live demo

[demo](www.google.com)

## Screenshots

[demo](www.google.com)

## Setup

```bash
cp .env.example .env
```

Populate `.env` with:

- `LLM_API_KEY` — currently **Groq** only (required for model `qwen/qwen3-32b`)

Then start the stack:

```bash
docker compose up --build -d
cd frontend && pnpm install
```

---

## Loading Dummy Data (optional)

Dummy data will **auto-load** on first startup if the database is empty.
You can also seed manually:

```bash
cd backend && make seed
```

This command initializes ClickHouse tables and populates test rows for local development.

---

## How to Start the App Locally

**Backend:**

```bash
cd backend && make dev
```

**Frontend:**

```bash
cd frontend && pnpm dev
```

---

## Example Prompts and Expected Outputs

**Request:**

```json
Show me statistics for all time from all sources. Add source and months to table.
```

**Response:**

```json
{
  "sql": "SELECT source, toStartOfMonth(date) AS month_start, sum(impressions) AS total_impressions, sum(clicks) AS total_clicks, sum(spend) AS total_spend, sum(conversions) AS total_conversions, sum(revenue) AS total_revenue, round((sum(clicks)/nullIf(sum(impressions),0))*100, 2) AS ctr_percent, round(sum(spend)/nullIf(sum(clicks),0), 2) AS cpc, round(sum(revenue)/nullIf(sum(spend),0), 2) AS roas, round((sum(conversions)/nullIf(sum(clicks),0))*100, 2) AS conversion_rate_percent, quantiles(0.25, 0.5, 0.75)(spend) AS spend_quantiles, quantiles(0.25, 0.5, 0.75)(revenue) AS revenue_quantiles FROM ad_performance GROUP BY source, month_start LIMIT 100",
  "data": [
    {
      "source": "facebook",
      "month_start": "2025-09-01",
      "total_impressions": 34905,
      "total_clicks": 1240,
      "total_spend": 900.7799911499023,
      "total_conversions": 35,
      "total_revenue": 1623.229965209961,
      "ctr_percent": 3.55,
      "cpc": 0.73,
      "roas": 1.8,
      "conversion_rate_percent": 2.82,
      "spend_quantiles": [
        97.84500122070312, 120.37000274658203, 152.2249984741211
      ],
      "revenue_quantiles": [
        168.9499969482422, 244.00999450683594, 277.6499938964844
      ]
    },
    {
      "source": "google",
      "month_start": "2025-09-01",
      "total_impressions": 21592,
      "total_clicks": 1246,
      "total_spend": 1470.5499954223633,
      "total_conversions": 46,
      "total_revenue": 2953.310028076172,
      "ctr_percent": 5.77,
      "cpc": 1.18,
      "roas": 2.01,
      "conversion_rate_percent": 3.69,
      "spend_quantiles": [
        161.79999542236328, 236.36000061035156, 248.4199981689453
      ],
      "revenue_quantiles": [
        323.6600036621094, 448.80999755859375, 496.55499267578125
      ]
    },
    {
      "source": "google",
      "month_start": "2025-10-01",
      "total_impressions": 60614,
      "total_clicks": 3585,
      "total_spend": 4250.03995513916,
      "total_conversions": 119,
      "total_revenue": 8641.429977416992,
      "ctr_percent": 5.91,
      "cpc": 1.19,
      "roas": 2.03,
      "conversion_rate_percent": 3.32,
      "spend_quantiles": [
        130.2400016784668, 189.7899932861328, 238.27999877929688
      ],
      "revenue_quantiles": [
        259.2949981689453, 357.3800048828125, 487.81500244140625
      ]
    },
    {
      "source": "facebook",
      "month_start": "2025-10-01",
      "total_impressions": 107555,
      "total_clicks": 3768,
      "total_spend": 2821.620014190674,
      "total_conversions": 101,
      "total_revenue": 5199.879959106445,
      "ctr_percent": 3.5,
      "cpc": 0.75,
      "roas": 1.84,
      "conversion_rate_percent": 2.68,
      "spend_quantiles": [87.85000228881836, 120, 152.97999572753906],
      "revenue_quantiles": [
        162.22000122070312, 209.99000549316406, 290.92498779296875
      ]
    }
  ],
  "summary": "From September to October 2025, Google outperformed Facebook in spend ($1,471–$4,250 vs. $901–$2,822), clicks (1,246–3,585 vs. 1,240–3,768), and ROAS (2.01–2.03 vs. 1.80–1.84), with higher conversion rates (3.69%–3.32% vs. 2.82%–2.68%). Google’s CTR was consistently higher (5.77%–5.91% vs. 3.50%–3.55%). Spend and revenue quantiles show Google’s higher median and upper quartile values, e.g., October spend quantiles: [130, 190, 238] for Facebook vs. [189, 236, 248] for Google. Data covers two months and two sources."
}
```

---

**Request:**

```json
Show me statistics for the last 2 months where the traffic source is google.
```

**Response:**

```json
{
  "sql": "SELECT SUM(impressions) AS total_impressions, SUM(clicks) AS total_clicks, SUM(spend) AS total_spend, SUM(conversions) AS total_conversions, SUM(revenue) AS total_revenue, ROUND((SUM(clicks) / nullIf(SUM(impressions), 0)) * 100, 2) AS ctr_percent, ROUND(SUM(spend) / nullIf(SUM(clicks), 0), 2) AS cpc, ROUND(SUM(revenue) / nullIf(SUM(spend), 0), 2) AS roas, ROUND((SUM(conversions) / nullIf(SUM(clicks), 0)) * 100, 2) AS conversion_rate_percent FROM ad_performance WHERE source = 'google' AND date >= addMonths(toStartOfMonth(today()), -2) AND date < toStartOfMonth(today()) LIMIT 100",
  "data": [
    {
      "total_impressions": 21592,
      "total_clicks": 1246,
      "total_spend": 1470.5499954223633,
      "total_conversions": 46,
      "total_revenue": 2953.310028076172,
      "ctr_percent": 5.77,
      "cpc": 1.18,
      "roas": 2.01,
      "conversion_rate_percent": 3.69
    }
  ],
  "summary": "For the last two months, Google traffic generated 1,246 clicks at a total spend of $1,470.55, with a click-through rate (CTR) of 5.77%. The return on ad spend (ROAS) was 2.01, driven by 46 conversions and $2,953.31 in total revenue. The average cost per click (CPC) was $1.18, and the conversion rate was 3.69%. Data aggregates across all campaigns; no quantiles or unique campaign counts are provided."
}
```

---

**Request:**

```json
Show me statistics for clicks for the last 2 months where the traffic source is facebook.
```

**Response:**

```json
{
  "sql": "SELECT sum(clicks) AS total_clicks, avg(clicks) AS average_daily_clicks, quantile(0.25)(clicks) AS clicks_q25, quantile(0.5)(clicks) AS clicks_median, quantile(0.75)(clicks) AS clicks_q75, count(*) AS days_with_data FROM ad_performance WHERE date >= addMonths(toStartOfMonth(today()), -2) AND date < toStartOfMonth(today()) AND source = 'facebook' LIMIT 100",
  "data": [
    {
      "total_clicks": 1240,
      "average_daily_clicks": 177.14285714285714,
      "clicks_q25": 128,
      "clicks_median": 187,
      "clicks_q75": 224.5,
      "days_with_data": 7
    }
  ],
  "summary": "For the last 2 months, Facebook drove 1,240 total clicks across 7 days with data. Average daily clicks were 177, with a median of 187, indicating moderate variability (25th percentile: 128, 75th percentile: 224.5). No spend, CTR, ROAS, or conversion data is included in the results."
}
```

## TODO

1. Redis caching redesign

   - Revisit caching strategy: remove persistent cache or limit with a short TTL.

   - Consider an ephemeral cache that stores only the user's most recent n queries.

2. LLM orchestration and SQL validation

   - Introduce layered SQL validation (nested aggregations, duplicate aliases, excessive grouping).

   - Split the LLM pipeline by responsibility:

     - model A — SQL generation;

     - model B — text summarization and explanation.

   - Add routing between providers (Groq, OpenAI, Claude, Qwen) depending on query type — analytical, narrative, or meta.

   - This reduces prompt length, improves accuracy, and cuts token costs.

3. Observability

   - Add Prometheus / OpenTelemetry metrics for LLM, SQL, and end-to-end latency.

   - Implement correlation IDs to trace requests through the entire stack.

   - Store structured JSON logs for centralized analysis.

4. Frontend improvements

   - Add persistent query history (localStorage or backend endpoint).

   - Implement toast notifications, theming (including dark mode), and responsive tables.

   - Optimize React Query GC and staleTime settings for short-lived sessions.

5. Future optimization

   - Introduce semantic prompt caching at the embedding level.

   - Preload ClickHouse explain plans for common queries.

   - Replace the FastAPI limiter with a Redis-based distributed limiter for better scalability.

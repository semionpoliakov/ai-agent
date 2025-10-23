# Frontend (Next.js)

Marketing Analytics Copilot UI built with Next.js App Router, React 19, React Query, and Tailwind CSS.

## Project structure

```
app/
  components/
    agent/             # Feature components for the agent experience
    data-table/        # Reusable data table wrapper
    providers/         # Client-side providers (React Query, etc.)
    ui/                # Primitive UI components (button, card, dialog, input, table, skeleton)
  config/              # Environment and runtime configuration guards
  lib/
    api/               # API client, schemas, error helpers
    hooks/             # Reusable React hooks
    utils/             # Browser utilities (rate limiter, CSV download)
  types/               # Shared TypeScript types and JSX namespace shim
  layout.tsx           # Root layout wiring fonts and providers
  page.tsx             # Server entry point that renders the agent console
  error.tsx            # App Router error boundary

public/
  ...
```

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | ✅ (at build time) | Base URL for the FastAPI backend, e.g. `http://localhost:8000`. Required for static generation and production builds. |

When the variable is omitted in non-production runs the UI falls back to `http://localhost:8000` and logs a console warning. Production builds **must** provide the variable or the build will fail fast.

You can create a `.env.local` with

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Scripts

```bash
pnpm install                    # install dependencies
pnpm dev                        # start Next.js dev server
pnpm lint                       # eslint (flat config with @next/next + unused-imports)
pnpm lint:fix                   # eslint --fix
pnpm typecheck                  # ensure route types exist then run tsc --noEmit
pnpm test                       # vitest run
NEXT_PUBLIC_API_BASE_URL=... pnpm build  # production build (env required)
pnpm analyze                    # build with bundle analyzer enabled
pnpm prettier:check             # prettier --check .
pnpm prettier:write             # prettier --write .
```

## Testing & QA pipeline

CI should run the scripts in this order:

1. `pnpm install`
2. `pnpm lint`
3. `pnpm typecheck`
4. `pnpm test`
5. `NEXT_PUBLIC_API_BASE_URL=... pnpm build`

## Design & state management

- React Query manages client-side mutations and cached responses (see `app/components/providers/react-query-provider.tsx`).
- `useAgentConsole` encapsulates local state, rate limiting, caching, and mutation lifecycle.
- Heavy client-only widgets (data table) are lazy-loaded with `next/dynamic` to keep the initial bundle lean.
- UI primitives live under `app/components/ui` for reuse across future routes.
- Runtime validation uses Zod to parse backend responses before storing them.

## Linting & formatting

- ESLint flat config (`eslint.config.mjs`) extends `typescript-eslint` type-checked presets and Next core web vitals.
- `eslint-plugin-unused-imports` removes dead imports or variables.
- Prettier 3 handles formatting (config in `prettier.config.cjs`).

## Tests

Vitest is configured with `vitest.config.ts`. The initial suite covers the rate limiter; add more tests for hooks/utilities as functionality grows. Test discovery matches `app/**/*.{test,spec}.{ts,tsx}`.

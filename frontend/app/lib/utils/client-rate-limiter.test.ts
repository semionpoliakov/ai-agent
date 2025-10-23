import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

import { ClientRateLimiter } from "./client-rate-limiter";

describe("ClientRateLimiter", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2024-01-01T00:00:00Z"));
  });

  test("allows up to the configured limit within the window", () => {
    const limiter = new ClientRateLimiter({ windowMs: 1000, maxRequests: 2 });

    expect(limiter.allow()).toBe(true);
    expect(limiter.remaining()).toBe(1);

    expect(limiter.allow()).toBe(true);
    expect(limiter.remaining()).toBe(0);

    expect(limiter.allow()).toBe(false);
    expect(limiter.remaining()).toBe(0);
  });

  test("resets after the window elapses", () => {
    const limiter = new ClientRateLimiter({ windowMs: 1000, maxRequests: 1 });

    expect(limiter.allow()).toBe(true);
    expect(limiter.allow()).toBe(false);

    vi.advanceTimersByTime(1000);

    expect(limiter.allow()).toBe(true);
  });

  afterEach(() => {
    vi.useRealTimers();
  });
});

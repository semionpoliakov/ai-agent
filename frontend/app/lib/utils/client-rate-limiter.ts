import { CLIENT_RATE_LIMIT_MAX_REQUESTS, CLIENT_RATE_LIMIT_WINDOW_MS } from "@/config/rate-limit";

interface RateLimiterOptions {
  windowMs?: number;
  maxRequests?: number;
}

export class ClientRateLimiter {
  private readonly windowMs: number;
  private readonly maxRequests: number;
  private timestamps: number[] = [];

  constructor({ windowMs, maxRequests }: RateLimiterOptions = {}) {
    this.windowMs = windowMs ?? CLIENT_RATE_LIMIT_WINDOW_MS;
    this.maxRequests = maxRequests ?? CLIENT_RATE_LIMIT_MAX_REQUESTS;
  }

  allow(): boolean {
    const now = Date.now();
    this.timestamps = this.timestamps.filter((ts) => now - ts < this.windowMs);
    if (this.timestamps.length >= this.maxRequests) {
      return false;
    }
    this.timestamps.push(now);
    return true;
  }

  remaining(): number {
    return Math.max(0, this.maxRequests - this.timestamps.length);
  }
}

export const rateLimiter = new ClientRateLimiter();

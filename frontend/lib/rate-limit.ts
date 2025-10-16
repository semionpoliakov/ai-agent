const WINDOW_MS = 15_000;
const MAX_REQUESTS = 3;

export class ClientRateLimiter {
  private timestamps: number[] = [];

  allow(): boolean {
    const now = Date.now();
    this.timestamps = this.timestamps.filter((ts) => now - ts < WINDOW_MS);
    if (this.timestamps.length >= MAX_REQUESTS) {
      return false;
    }
    this.timestamps.push(now);
    return true;
  }

  remaining(): number {
    return Math.max(0, MAX_REQUESTS - this.timestamps.length);
  }
}

export const rateLimiter = new ClientRateLimiter();

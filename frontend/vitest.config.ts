import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  test: {
    environment: "node",
    include: ["app/**/*.{test,spec}.{ts,tsx}"],
    globals: true,
    coverage: {
      reporter: ["text", "lcov"],
      reportsDirectory: "coverage",
      include: ["app/**/*.{ts,tsx}"],
      exclude: ["**/*.d.ts", "**/*.test.*", "**/*.spec.*"],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "app"),
    },
  },
});

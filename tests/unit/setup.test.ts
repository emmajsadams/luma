import { afterEach, expect, test, vi } from "vitest";
import { setupAvailable } from "../../lib/setup";
afterEach(() => vi.unstubAllEnvs());
test("setup is unavailable for absent, partial or whitespace-only configuration", () => {
  vi.stubEnv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "");
  vi.stubEnv("CLERK_SECRET_KEY", "");
  vi.stubEnv("NEXT_PUBLIC_CONVEX_URL", "");
  expect(setupAvailable()).toBe(false);
  vi.stubEnv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "synthetic");
  expect(setupAvailable()).toBe(false);
  vi.stubEnv("CLERK_SECRET_KEY", " ");
  vi.stubEnv("NEXT_PUBLIC_CONVEX_URL", "https://example.test");
  expect(setupAvailable()).toBe(false);
});

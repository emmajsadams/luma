// Server-only configuration check. Absence never grants a session.
export function setupAvailable() {
  return Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim() && process.env.CLERK_SECRET_KEY?.trim() && process.env.NEXT_PUBLIC_CONVEX_URL?.trim());
}

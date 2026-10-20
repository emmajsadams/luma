import type { AuthConfig } from "convex/server";
// Missing issuer config deliberately installs no trusted token provider.
export default {
  providers: process.env.CLERK_JWT_ISSUER_DOMAIN ? [{ domain: process.env.CLERK_JWT_ISSUER_DOMAIN, applicationID: "convex" }] : [],
} satisfies AuthConfig;

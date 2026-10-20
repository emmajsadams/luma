# Authentication and persisted tasks (issues #3 / #5)

This slice replaces the demo with Clerk sign-in/sign-up and account controls (including sign-out), and reactive Convex task list/add/toggle/delete. Notes/calendar are explicitly unavailable, not fake data. MCP transport is not implemented; API paths are protected by proxy and unconfigured requests receive 503. Future handlers must additionally check auth at the resource and reuse owner-scoped Convex functions.

## Configuration — no credentials are included

Provide these in the local ignored `.env.local` or your hosting environment secret store:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: publishable key from the intended Clerk instance.
- `CLERK_SECRET_KEY`: secret key from that same instance; never expose it to the browser.
- `NEXT_PUBLIC_CONVEX_URL`: intended Convex deployment URL. Public, not an admin credential.
- `CONVEX_DEPLOYMENT`: CLI deployment selection, supplied by official Convex setup.

On the matching Convex deployment configure `CLERK_JWT_ISSUER_DOMAIN` to that Clerk instance's Frontend API URL. Activate the Convex integration in Clerk (audience/application ID `convex`). Sync auth configuration and functions with `pnpm exec convex dev` for development. Missing issuer installs no trusted providers: unauthenticated function calls still throw. Missing Next-side configuration displays only Setup unavailable; it does not activate demo or localStorage persistence. Configuration presence is not proof that credentials or deployment are working.

Official references consulted:
- https://docs.convex.dev/auth/clerk
- https://clerk.com/docs/reference/nextjs/clerk-middleware

Installed Next 16 uses `proxy.ts`; Clerk provider wraps ConvexProviderWithClerk with Clerk's `useAuth`. Data queries wait for `useConvexAuth`, not merely Clerk session state. Server task rendering checks `auth.protect()` as well as proxy protection. Backend authorization derives ownership exclusively from verified identity `tokenIdentifier`, never supplied owner IDs. Date-only task due dates are validated separately from timestamps. There is no notes/events persistence in this slice.

## Registration policy

Registration can be public in Clerk; each account sees only its own data. This is not a single-user allowlist. For a personal-only deployment the owner should configure Clerk restricted/invitation-only registration before opening access. No guessed identity or email allowlist has been added.

## Local code generation

Generated files are official CLI output, not fabricated bindings. With no cloud credentials this work used the supported anonymous local backend:

    CONVEX_AGENT_MODE=anonymous pnpm exec convex dev --once --typecheck disable
    CONVEX_AGENT_MODE=anonymous pnpm exec convex codegen --typecheck disable

This creates ignored `.env.local` deployment selection and local backend state. It does not establish a Clerk session, configure a cloud deployment or demonstrate real login. Codegen may contact this local backend. Commit `_generated` files but never `.env*`, local state, credentials or sessions. Normal contributors with a configured deployment use `pnpm exec convex codegen`.

## Verification and remaining release gate

Local unit tests use convex-test identities, not real JWT signature validation. They cover anonymous access to all task operations, cross-owner mutation denial, issuer-separated identities, CRUD, missing records, forged ownership arguments and input validation. Setup configuration has a RED→GREEN whitespace/partial configuration regression. Initial backend test collection failed before schema implementation, then passed after implementation.

Browser tests intentionally run with Clerk configuration absent. Desktop and mobile verify all page routes show setup-unavailable, no task controls, no horizontal overflow, accessible layout, static PWA assets and API denial. The shared fixture fails on console/page errors. Screenshots are local ignored test-results artifacts. These are NOT signed-in browser tests.

Before any deployment claim:
1. Use approved separate development/preview Convex and Clerk instances; never point previews at production data. Configure matching keys and issuer using secret stores, then sync backend and rebuild Next (public variables are build-time).
2. In a real browser register/sign in, add/toggle/delete tasks, reload and reconnect, and confirm persistence and reactive updates across two tabs.
3. Sign out and verify no task data remains visible; verify direct protected URLs and API calls without cookies/tokens are denied.
4. Use two real accounts and attempt cross-owner IDs directly against Convex; verify denial, including after switching accounts and token expiry.
5. Capture desktop/mobile traces, console/page errors and exact tested commit SHA. Verify invalid/missing issuer fails closed.
6. Complete independent exact-head review and CI before merging. Hosting/authenticated MCP end-to-end remain issue #5 work. No production resources or paid services were provisioned by this slice.

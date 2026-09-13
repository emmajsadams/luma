# Luma architecture and delivery plan

Luma is a cozy, sci-fi personal home for tasks, notes and calendar, and a testbed for an issue-driven software factory.

## Product
- Next.js App Router + TypeScript + responsive accessible UI hosted on Vercel.
- PWA manifest, icons, standalone display and mobile install instructions. Installability does not imply offline writes. First version is online-first; offline status must be explicit. Never cache authenticated responses indiscriminately.
- Convex stores tasks, notes, events and user preferences, provides reactive UI queries and enforces ownership server-side.
- Next.js `/api/mcp` hosts a Streamable HTTP MCP resource server on Vercel, delegating domain work to the same Convex functions. No separate always-on server is needed for ordinary request/response tools.
- Browser sessions and MCP client authorization are separate integration surfaces. Prefer managed authentication; prove issuer/audience/subject mapping in a spike. Never assume a browser JWT is a suitable MCP access token or forward an arbitrary token to Convex. No admin key on user data paths.

## Data contracts
- Tasks: owner, title, description, status (todo/in_progress/done), priority, optional date-only dueDate (YYYY-MM-DD), createdAt, updatedAt, version.
- Notes: owner, title, Markdown body, createdAt, updatedAt, version. Sanitize rendered content.
- Events: owner, title, description, UTC start/end milliseconds + IANA timezone; separately represent all-day local date ranges. End must follow start.
- Optional links validate same-owner targets. All lists/search are paginated and owner-filtered, never filter after exposing data.
- Mutations use conflict/version handling where concurrent overwrites matter. MCP create operations need retry idempotency. Deletion starts with trash/restore rather than irreversible removal.

## MVP sequence (canonical acceptance lives in linked GitHub issues)
1. [Factory foundation](https://github.com/emmajsadams/luma/issues/1): contracts, issue templates, CI, browser evidence.
2. [PWA shell](https://github.com/emmajsadams/luma/issues/2): working responsive shell and test infrastructure, explicitly labeled demo if backend not connected.
3. [Convex backend](https://github.com/emmajsadams/luma/issues/3): owner-scoped CRUD and denial tests, then authenticated UI integration.
4. [MCP](https://github.com/emmajsadams/luma/issues/4): domain parity, tool discovery, CRUD/search tests, auth failures, scope enforcement. Depends on backend/auth.
5. [Deployment](https://github.com/emmajsadams/luma/issues/5): real Vercel/Convex/auth configuration and end-to-end verification. Preview backends use synthetic data, not production copies.

Defer external calendar sync, recurring rules, push reminders and true offline conflict resolution until the base system is reliable. Calendar MVP means Luma-owned events, not automatic Google/Apple sync.

## Development and verification
`pnpm install --frozen-lockfile`; `pnpm lint`; `pnpm typecheck`; `pnpm test`; `pnpm build`; `pnpm exec playwright install chromium`; `pnpm test:e2e`.

Backend development adds `pnpm exec convex dev` after an authorized project exists. CI unit tests should use convex-test without production secrets. Vercel builds integrate `convex deploy` using separately scoped preview/production deployment keys, following current Convex documentation. Deployment configuration is not established merely by committing this document.

## Sources
- https://nextjs.org/docs/app/guides/progressive-web-apps
- https://docs.convex.dev/production/hosting/vercel
- https://docs.convex.dev/auth/clerk
- https://github.com/vercel/mcp-handler

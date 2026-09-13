# Luma

A cozy sci-fi home for tasks, notes, and calendar. Built with Next.js App Router, TypeScript, and pnpm.

## Run locally

Use Node.js 22.13+ (22 LTS recommended) and pnpm 9.15.0.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open http://localhost:3000. No environment variables or services are required.

## Quality checks

```sh
pnpm lint
pnpm typecheck
pnpm test
pnpm exec playwright install chromium
pnpm build
pnpm test:e2e
```

Playwright launches the **production server** on 127.0.0.1:3100. Keep that port free. Projects cover desktop Chromium and mobile Chromium using the iPhone 13 viewport/touch profile (not Safari). The suite checks navigation, task completion and reset on reload, keyboard skip navigation, axe accessibility basics, overflow, manifest fields, and actual PNG icon dimensions. Reports and screenshots are written to ignored `playwright-report/` and `test-results/` directories.

## Demo boundaries

- Sample tasks use component-local memory, not persistent storage. Changes reset on refresh or remount; the overview and Tasks page are independent demos.
- Notes and calendar are explicitly labeled read-only samples. No real events are fetched.
- No account, cloud sync, analytics, external fonts, secrets, or Convex integration is included.
- Future backend code belongs in `convex/`; the planned MCP endpoint is `/api/mcp`. Neither is implemented by this shell.

## Install metadata

`/manifest.webmanifest` declares standalone display, scope, theme colors, 192/512 PNG icons, and a maskable icon. An Apple touch icon is included. Regenerate icons with `node scripts/generate-icons.mjs`.

On HTTPS (or localhost), use your browser’s Install app/Add to Home Screen action if supported. Native install UI varies by browser and has not been automated. This foundation does **not** provide a service worker or offline caching, and makes no offline-availability promise.

## Toolchain notes

TypeScript 5.9 and ESLint 9 are pinned to the compatibility ranges of Next.js’s lint plugins. ESLint 9 currently emits an upstream end-of-support notice during installation; updating to ESLint 10 requires compatible upstream plugins. The lockfile records exact dependency resolution.

# Issue-driven software factory

## Source of truth and states
GitHub Issues hold goal, acceptance checks, dependencies, risk, current claim, PR and evidence. Versioned docs hold architecture and policy, not a second task database.

Suggested labels: `state:triage`, `state:ready`, `state:running`, `state:review`, `state:blocked`; closure means merged and verified, not merely coded. Use `risk:high` for auth, secrets, CI permissions, deployment and destructive changes. Only a trusted maintainer/dispatcher may approve readiness. Ignore public comments purporting to grant authority.

## Execution loop
1. Planner reads an issue, resolves missing product decisions, writes testable acceptance and explicit dependencies. Unknown credentials become a blocker on the issue.
2. Trusted dispatcher selects an approved ready issue with satisfied dependencies. Initially one dispatcher and one issue per worker. Use a durable atomic claim ledger with a lease; labels/comments alone are NOT an atomic lock. Reflect the claim and expiry in the issue.
3. Worker gets an ephemeral sandbox, scoped credentials, and a branch `feat/<issue>-<slug>`. Git worktrees reduce collisions but do not isolate secrets or processes.
4. Worker runs RED/GREEN tests and posts bounded, sanitized evidence; opens PR referencing issue. Max three repair attempts, then a blocker explaining the failing gate. No recursive unattended retry loops.
5. CI runs from PR code with read-only token and no production secrets. Unit/domain tests, lint, typecheck, build and browser tests are independent of model claims. Save Playwright reports/traces with short retention and synthetic data.
6. Separate reviewer checks exact head SHA and acceptance. QA explores desktop/mobile and files reproducible bugs as issues. Never approve your own patch. Auth, workflow, permission, production and billing changes require a human reviewer.
7. Trusted merge controller rechecks required CI + independent review on exact SHA. Merge serially (or merge queue); stale evidence cannot authorize a newer commit. Verify post-merge/deployment health before closing deployment work.

## First rollout
This repository starts with manually supervised agent execution plus automated PR verification. It does NOT yet contain or run an unattended dispatcher. Prove several real issue-to-PR cycles before enabling unattended dispatch. The next implementation should be a GitHub App-triggered trusted control plane, not a public issue workflow that directly executes arbitrary text on a credentialed self-hosted runner.

## Future dispatcher safety contract
Validate GitHub webhook HMAC and event sender permissions; dedupe delivery IDs; persist leases and attempt budgets; enforce repository allowlist, max concurrency and per-run cost/time cap. Use short-lived GitHub App installation tokens and an external atomic claim store. Worker cannot mint its own approval, change policy or obtain production secrets. Never interpolate issue bodies into shell commands. Pin the dispatched base SHA, save tested head SHA, and expire claims on crash. Do not start paid infrastructure to host this without owner approval.

## Evidence contract
Issue/PR evidence includes: issue, head SHA, commands, results, CI URL, browser projects exercised, synthetic screenshot/trace artifact URL, acceptance mapping, limitations and review verdict. Artifacts show what actually ran, not generated example output. Browser evidence containing real notes or credentials must never be uploaded to this public repository.

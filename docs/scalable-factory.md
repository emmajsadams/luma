# Scalable Luma factory: proposed architecture

Status: design proposal, not a deployed multi-worker service. The existing 15-minute Hermes cron remains single-worker until the migration gates below pass. GitHub Issues are the product source of truth; an execution ledger is operational state, not a competing backlog.

## Prior art inspected

- OpenAI Symphony: https://github.com/openai/symphony and https://github.com/openai/symphony/blob/main/SPEC.md . Issue-driven isolated autonomous runs, reconciliation/retries and proof of work. Reference demo uses Linear; reference implementation is Elixir. README explicitly calls it a trusted-environment engineering preview. Learn lifecycle and recovery semantics; do not assume GitHub/Hermes are drop-in adapters.
- Agent Orchestrator: https://github.com/Untrivial-ai/agent-orchestrator . The former https://github.com/ComposioHQ/agent-orchestrator redirects here. Current README describes a local desktop/daemon architecture with per-worker branches/worktrees, planning orchestrator, PR/CI/review tracking and feedback to workers. A stronger candidate for reuse than writing a dashboard or terminal multiplexer. Current API, Hermes integration and unattended GitHub intake need a runnable spike before adoption.
- Hermes CLI/worktrees/security: https://hermes-agent.nousresearch.com/docs/user-guide/git-worktrees and https://hermes-agent.nousresearch.com/docs/user-guide/security . Existing harness can execute worker sessions; a worktree is not a security sandbox. Short in-process delegations are not durable workers.

These are documented capabilities, not products we have installed/benchmarked for Luma. Do not compare against stale snippets from the old AO namespace.

## Decision

Use one logical deterministic control plane, many bounded implementation sessions, an independent review pool, and one merge controller per repository. Start with two builders and one reviewer, one merge at a time. Planners can be LLM sessions but cannot claim work or authorize merge independently of the controller. Multiple physical controller replicas may run only once transactional leases/fencing are implemented.

Prefer adopting an existing runtime/orchestrator if a spike proves GitHub intake, Hermes execution, exact-head review, recovery and credential separation. Otherwise build a thin TypeScript service under factory/, not a general-purpose agent desktop. Do not let this infrastructure project indefinitely delay the basic Luma product.

## Flow

GitHub issue -> trusted intake/planning -> dependency-ready queue -> atomic claim -> isolated builder -> PR -> CI + independent adversarial review -> repair on same issue branch -> serial merge -> post-merge/deployment verification -> issue closure.

Review is a distinct job keyed by PR head SHA. A new commit invalidates prior review. An issue's execution state is not inferred merely from an agent saying done.

## Authority and intake

Emma can create issues from GitHub; owner-authored issues within the approved Luma scope are eligible for automatic triage. Well-specified work can become ready without a second manual ceremony. For outside authors, require a trusted maintainer approval bound to issue ID and revision. Validate actor permissions via API, not display names or text. Labels are presentation, not authentication or atomic locks. Treat issue/comment bodies, code comments and browser pages as untrusted data.

Planner writes goal, acceptance, non-goals, dependencies, risk, likely affected areas and implementation budget to the GitHub issue. It can create explicitly linked child issues for independently mergeable work; it cannot unilaterally approve unrelated scope. Conflicting architectural decisions are settled once in versioned docs and repeated in affected issue specs. Genuine unknowns become needs-review with one precise @emmajsadams comment. Dedupe by blocker signature; other work continues.

## Control-plane schema (proposed)

Use a separate factory control-plane database, never the personal task data tables. Initial single-host adapter may use SQLite transactions; distributed implementation uses a transactional store (a separate Convex project is compatible with the preferred stack).

- jobs: repositoryId, issueId, approvedRevisionDigest, kind (implement/review/verify), candidateSha?, state, priority, dependencyIds, attemptCount, nextEligibleAt.
- leases: jobId unique, workerId, fence monotonic integer, expiresAt, heartbeatAt. Claim atomically checks readiness, expiry, concurrency and increments fence. Completion/heartbeat require the same fence; stale workers cannot publish or merge.
- runs: runId, jobId, fence, baseSha, headSha, branch, workspaceId, sessionId, start/end, exitReason, token/cost counters, checkpoint.
- reviews: repositoryId, prNumber, headSha, reviewerRunId, verdict, findings, evidence. Unique logical review role per candidate SHA; retain superseded evidence but never accept it for a new SHA.
- deliveries: webhookDeliveryId unique for dedupe; outbox operation key unique for idempotent GitHub comments/checks/PR creation.

Worker execution is at-least-once, not magically exactly-once. External effects use idempotency plus readback reconciliation. On uncertain push/PR creation, look up branch and issue linkage before retrying.

## Scheduling and recovery

Use GitHub webhooks for low latency, validate HMAC, delivery ID and immutable repository ID. Poll every 60 seconds as reconciliation fallback. Keep the existing 15-minute cron only as a watchdog after cutover, not a second dispatcher. Persist process/session IDs and checkpoints outside conversation memory.

Suggested initial limits: two builders, one review worker, one merger; 30-minute attempt budget, 60-second heartbeat, five-minute lease, three repair attempts per failure signature with exponential backoff. These are proposed policy defaults, not currently configured infrastructure. Long jobs checkpoint and renew leases, then resume or restart with issue/branch/test evidence. Kill expired worker process groups and reject their stale results using fencing. Preserve failed workspaces for bounded diagnosis with no secrets in public artifacts.

Partition code areas to avoid collisions. Shared hotspots (package manifest/lockfile, schema, auth, routing, tokens) require a scheduler resource lock or serial integration. Parallel UI/backend jobs agree on contracts first. Leases in memory, issue labels and worktrees alone are insufficient.

## Worker sandbox and credential split

A builder receives an ephemeral container/VM with repository checkout, bounded inference access and disposable test data. No Emma home, Keychain, SSH agent, production deployment key or unrestricted Docker socket. Build/test code is untrusted. Network egress is explicitly allowed only as needed.

Controller owns repo-scoped short-lived GitHub App tokens for publication. Review runner executes tests in a sandbox but has no repository write/merge or production credentials. Publisher validates candidate patches and branch SHA; merger alone can merge. Production deployment secrets stay in a separate trusted deploy job. No privileged pull_request_target execution of candidate code. Separate processes using the same broad local credential are logical separation only, not a security boundary.

## Adversarial review protocol

Provide a fresh reviewer with the issue acceptance, base/head SHA, diff, repository policy and CI/browser artifacts. Do not provide the builder's reasoning transcript as evidence. Reviewer should try to falsify the implementation's claims, not praise effort or generate speculative complaints.

Roles:
- Correctness/spec reviewer: missing acceptance, regressions, edge cases, state and concurrency, dates/timezones, stale updates, retry idempotency.
- Security reviewer for auth/data/MCP: cross-owner reads/writes/search, token issuer/audience/scopes, injection, secrets, schema validation, unsafe external actions.
- Browser QA: tasks/notes/events CRUD, reload/persistence, mobile/desktop/WebKit, keyboard/focus, errors and poor-network behavior, synthetic data only.

One reviewer can perform the first role initially; allocate dedicated security/browser review jobs for relevant changes. Use a different model where practical to reduce correlated blind spots, not as a guarantee of independence.

Structured finding: severity, file/line or route, violated acceptance/invariant, reproducible steps or failing test, impact and suggested remedy. Verdict PASS, CHANGES_REQUIRED or BLOCKED. Findings must be grounded; lack of test coverage is distinguished from a demonstrated defect. Reviewer should add a failing regression test on its review branch or attach a patch, not silently modify the candidate. Builder repairs; fresh head triggers new review. CI is deterministic evidence and cannot be replaced by model agreement.

## Merge contract

Only merge if latest remote head equals tested/reviewed head, all required CI passes, independent verdict is PASS, no unresolved blocking findings, dependencies are satisfied, and branch is current with base or passes merge-queue testing. Serialize merges; base changes invalidate integration evidence. Do not rely on mutable natural-language 'approved' comments; controller validates structured review receipts from registered reviewer runs and writes a check for the exact SHA.

Owner already authorized routine merges and hosting. No repetitive approval request for ordinary verified work. Human boundary remains destructive production changes, new paid commitments beyond authorized hosting, unresolved product decisions, security uncertainty or failed repair budget. Tag needs-review and @emmajsadams on the relevant issue/PR once per new blocker. Close only when acceptance is truly complete; deploying a demo shell does not complete backend/MCP issues.

## Repository layout to implement

factory/README.md; factory/config.schema.json; factory/config.json; factory/src/{controller,intake,leases,runner,publisher,review,merge,github}.ts; factory/prompts/{planner,builder,reviewer,browser-qa}.md; factory/tests/; docs/scalable-factory.md. Checked-in config is non-secret; credentials remain in ignored env files or secret stores. Operational run state is not committed.

## Rollout and acceptance

1. Adoption spike: test AO and Symphony fit on a disposable repository, verify real Hermes adapter/run capability, crash recovery, license and maintenance costs; record decision before implementing duplicate infrastructure.
2. Controller in dry-run mode: replay saved synthetic events; unit tests for competing claims, expiry, fencing, dedupe, changed approved revision, attempt budget, dependencies and outbox reconciliation.
3. Two-worker sandbox trial: concurrent distinct issues, one deliberate shared-file collision; crash one worker, restart controller, prove no duplicate PR or stale completion.
4. Independent review trial: intentionally seeded auth/ownership bug and browser regression; require concrete failing evidence, repair and new-SHA review. Test malicious issue text cannot expose secrets.
5. Merge trial: stale approval/new commit, failed CI, changed base, missing evidence all block; exact-head green/reviewed PR merges once. Read back merged SHA and post-merge checks.
6. Cutover: pause old implementation cron, migrate active claims/PRs, start exactly one new controller, then enable watchdog-only cron. Do not run both dispatchers.
7. Scale only after successful trials: additional runners, then replicated controllers with durable distributed leases. Record cost, throughput, retries, escaped defects, review reversals and time-to-merge rather than optimizing agent count alone.

No extra workers or replacement service are launched by this document.

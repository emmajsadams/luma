# Native factory and swarm boundaries

Summary of the read-only local architecture/security audit of 2026-10-13
(installed Hermes source `f88c6fc46e`), not a new activation decision. GitHub issues
#10 and #11 remain canonical; this document neither replaces their full acceptance
nor creates a competing backlog. The adapter is blocked staging only.

## No automatic swarm activation

The audited public `hermes kanban swarm` command creates an immediately dispatchable
graph: it completes the root and releases dependent workers. It has no atomic
blocked-draft option. Creating then blocking is a race; a separate board is not a
dispatch pause. Do not invoke swarm to stage work. Ordinary tasks can be created
blocked and unassigned with explicit routing; any future graph mutation or release
requires separate authorization and admission checks. The adapter's two real
saved-ID retries succeeded with zero runs; that is not execution approval.

## Roles and responsibilities

- Builders: eventually at most two, each with isolated worktree, ports, test data,
  credentials and explicit routing; serialize shared-file hotspots. Prove one
  integrated lifecycle before admitting concurrent builders.
- Independent verifier sessions: correctness, security and browser review against
  the exact head, curated issue/diff/test evidence, registered actual identities,
  and no builder reasoning transcript or merge credentials. Persist structured
  grounded findings and bounded repair rounds; every new head invalidates review.
- Serialized merge authority: a single isolated credential holder, not a builder
  or swarm synthesizer. Revalidate approved scope, current head and base/merge-queue
  candidate, trusted required CI and independent verdicts immediately before a
  SHA-conditioned merge; read back the result. Head/base changes invalidate evidence.

## Reuse native lifecycle; keep policy in a thin bridge

Audited native primitives include atomic task claims, run IDs/claim tokens,
cooperative completion fencing, PID/start-time crash checks, reclaim/circuit
breakers and local per-board dispatch locks. Reuse these rather than building a
second scheduler. Durable task context does not prove exact conversation resume;
macOS kill/restart recovery still needs an execution trial.

Custom glue remains necessary for GitHub revision authority and dependencies,
durable intent/receipt reconciliation for uncertain external effects, approval
revalidation, publication/session receipts, trusted reviewer registration, bounded
feedback escalation, and deterministic serialized merge policy. Native database
fencing does not fence an already-issued push/PR/merge. Webhook ingress, if added,
needs signature verification and delivery dedupe alongside reconciliation polling.
Keep control-plane state separate from personal Luma data and retain one intake path.

Swarm's prompt-level verifier verdict is not a kernel-enforced review gate;
terminal/archived parents can release children. Native PR acceptance checks useful
exact-head CI conditions, but does not establish reviewer independence, tested
current base, serial merge authorization or post-completion invalidation. A task
marked done, a local probe count or a stale-head verdict file is not factory delivery.

## Isolation and runtime gaps

Profiles/workspaces and fresh sessions are not whole-worker OS sandboxes. Same-UID
filesystem, shell, keychain and GitHub access remain concerns. Before multiworker
execution, demonstrate least-privilege credential confinement, authenticated narrow
bridges, fenced external effects and independent reviewer artifact boundaries.
The dirty reserve controller is not a verified replacement; it remains preserved.

The audit observed gateway dispatch enabled and concurrency caps unset; unset caps
are memory-derived defaults, not a two-builder limit. CLI warns running gateways
may still load pre-update code. Resolve that mismatch with separate authorization;
no service restart or configuration change is part of staging.

## Routing is role-specific, not implied

Audit-resolved default-profile configuration was `openai-codex/gpt-6.1-sol`, low
reasoning, with no reasoning overrides. This is configuration evidence, not an
inference availability test or attestation of loaded gateway settings. The adapter
pins `openai-codex/gpt-6-astra`; the reserve runner also pins that model for both
roles. Interactive model selection, adapter pins and gateway defaults are distinct.
Swarm supplies profiles without per-role model/provider/reasoning overrides. The
public create CLI did not expose reasoning although the dispatcher supports it.
Explicit supported role routing/reasoning policy and availability must be verified
before activation, including any goal-judge/delegation inference. No other profiles
were changed; future profile policy requires separate inspection and approval.

## Full acceptance is still required

Issue #10 (depends on #9) retains selected-runtime implementation, atomic fenced
claims, webhook verification/dedupe plus reconciliation, bounded retries, durable
sessions/checkpoints, two-builder cap, sandboxed credentials, hotspot serialization
and separate control-plane state. Real concurrent-claim, worker-crash,
controller-restart, stale-completion, duplicate-webhook and uncertain-PR-creation
trials remain mandatory. Verify old implementation cron is paused before enabling
one replacement intake/controller; no multiworker claim without real trial evidence.
Owner lifecycle requirements also retain latest-main worktrees, unique local test
environments, meaningful issue updates/commits, PR publication and restart resumption
of existing work rather than duplicate claims.

Issue #11 (depends on #10) retains fresh independent correctness/security/browser
sessions, reproducible structured findings, exact-SHA registered reviewer verdicts,
no builder transcript/merge credentials, invalidation on changes, deterministic CI
plus current-base/merge-queue testing before serial merge. Seed ownership and browser
bugs and prove detection/repair; demonstrate failed CI and stale reviews prevent an
actual merge call. Preserve the three-round repair bound and deduplicated
`needs-review` owner escalation for unresolved findings or true human blockers.
Routine green reviewed merges require no added ceremony, but staging authorizes
none of these operations. Full issue text/comments remain authoritative.

# Hermes-native Luma factory: recovery and decision proposal

Status: proposed, not installed. This supersedes the assumption that we must finish the bespoke controller. Luma remains the Next.js/Convex personal tasks, notes, calendar and MCP product.

## Verified recovery state
- No Luma builder/controller process appeared in pgrep inspection; no Luma/factory label appeared in the logged-in user's launchctl list. Hermes gateway/dashboard were present. This is not an audit of every system launch domain.
- Active HERMES_HOME is /Users/emma/.hermes. `hermes cron list` now reports no scheduled jobs, unlike earlier thread state. Do not recreate the previous job without reconciliation.
- `hermes webhook list` reports platform disabled. Only default profile exists. No profiles, safeguards, plugins, services or jobs changed by this recovery run.
- Controller worktree preserved, including uncommitted README/config/controller/runner/service/tests and untracked tests/docs. Latest checkpoint 23bae66 follows 1a09bac and 5d03994. No controller PR is open; architecture PR12 is open.
- Executed `uv run --with pytest python -m pytest factory/tests -q`: 98 passed, 1 failed. Failure: test_private_directories_do_not_chmod_existing_ancestors in test_service.py; bootstrap_launchd changes an existing ancestor's permissions. Do not install it.
- No live issue-to-merged-PR controller cycle or restart recovery verified. Existing local tests are reusable evidence, not installed orchestration.

## Recommendation
Use Hermes as the execution/lifecycle engine, GitHub as the canonical scope/evidence surface, and a thin GitHub bridge. Prefer native Kanban as an INTERNAL durable execution queue, conditional on Emma accepting this distinction from a second product backlog and on a disposable compatibility probe. Do not implement a competing general queue/session manager/daemon first.

GitHub issue -> deterministic authenticated bridge -> native durable execution task -> Hermes builder session/worktree -> independent review task -> exact-head CI/merge gate -> GitHub evidence/status.

GitHub owns acceptance, approval revision, decisions, PR and completion. Kanban would own only execution attempts, claims, dependencies, worker handles, heartbeats and recovery. Mirror issue IDs/URLs and approved revision digest. Never edit scope independently on both surfaces. A completed internal task does not automatically close its issue.

## Native vs custom
| Concern | Owner / evidence | Missing bounded work |
| --- | --- | --- |
| Session history/resume | Native SQLite sessions; installed chat supports --resume, --continue, --create-if-missing, --in, --query-file, budgets | Bridge stores exact session ID per role/issue; verify resume after process death |
| Role procedures | Native skills and AGENTS.md | Repo-versioned builder/reviewer/QA skills; validate readiness, no global mutation of other profiles |
| Durable claims/workers/recovery | Native Kanban documents durable rows, OS-process workers, retries/handoffs; installed CLI advertises family | Disposable probe of actual claim/reclaim, review lifecycle and completion contracts BEFORE relying on them; no direct SQL writes |
| Short review fanout | Native delegate_task | Useful within live run, NOT durable queue; separate reviewer task/session for restartable review |
| Periodic discovery | Native no-agent cron | Five-minute reconciliation invokes deterministic intake, not a fresh LLM trying to finish whole feature each tick; verify actual installed runtime limits instead of stale skill numbers |
| Event ingress | Native webhook subscription/signatures/filtering | GitHub actor/revision approval, dedupe and issue-to-task idempotency; poll-first avoids opening public endpoint |
| Integration surface | Native plugin tool/hook system | Small repo-owned bridge plugin or script, compatibility validation; keep disabled until reviewed |
| Worktrees | Native support + git | Latest-main SHA, deterministic reuse, unique ports/test data and cleanup contract; worktree is not credential isolation |
| Merge safety | GitHub checks + native contract where validated | Verify current head/base, separate reviewer identity/verdict, required repository approvals, serial merge; reuse tested custom gates only if native coverage missing |
| Review budget | Durable role workflow | Persist three feedback rounds separately from execution retries; after cap needs-review and deduped owner mention |

## Why this changes the previous approach
The bespoke attempt duplicated lifecycle logic while ignoring native durable task execution. A saved chat session is resumable history, not a scheduler; a cron prompt is a wakeup, not a complete worker supervisor; delegation is process-local. Combining the correct native primitives reduces custom failure paths without claiming they automatically implement GitHub authority or exact-head reviews.

Symphony/AO remain prior art, not a committed runtime choice. Installing another orchestrator before testing Hermes native execution would add another lifecycle owner. Reconsider them only if the native probe identifies a concrete unsupported requirement.

## Security and approval compatibility
The current single-query session blocked a script-execution command; simpler read-only commands worked. This is real evidence that unattended tooling/approval compatibility needs testing, not a reason to disable safeguards. Installed root `hermes -z` help says it bypasses approvals; do NOT use that shortcut. Use regular `hermes chat --query-file ... --oneshot` with approved policy. No --yolo or blanket approval changes.

Profile isolation is not OS credential isolation. Keep trusted owner-only single-worker mode first; containerize the whole worker or use an unprivileged runtime before outside contributors or broader parallelism. No production keys in builder/reviewer. Independent review is a new session, not self-authored PASS text. Every new head invalidates verdict/CI; three unresolved feedback rounds escalate with needs-review and @emmajsadams. Do not merge unresolved security defects because bots mostly agree.

## Bounded next probe (not activated in this run)
1. Emma decides whether an internal native Kanban execution queue is acceptable; alternative is GitHub + thin lease/session supervisor with more custom recovery burden.
2. On a disposable board/workspace, validate task create/claim, latest-main worktree and role handoff with installed supported interfaces; no default production board mutation.
3. Kill/restart a synthetic worker, verify no double claim or stale completion, then resume actual Hermes session under unchanged safeguards. Test blocked-command propagation and model/provider availability.
4. Bind one harmless owner-approved GitHub issue to one native execution task; deterministic fixture replay proves duplicate events/changed scope do not spawn extra work.
5. Run builder -> fresh reviewer -> deliberate finding -> repair -> exact-head CI -> merge. Verify three-round stop and changed-head rejection.
6. Only then activate one intake path. Recheck cron/services and migrate existing branches; no concurrent bespoke dispatcher. Keep public GitHub evidence separate from private session data.

## Preserve/reuse
Do not delete or overwrite uncommitted controller work. Candidate reusable pieces: GitHub approval checks, exact-head gates, review-round tests, environment/path safety regression tests. Keep existing controller disabled; avoid spending more effort on its launchd service/queue until native gap is demonstrated. Do not claim every test can be reused unchanged across a different adapter.

## Decisions for Emma
- Recommended: GitHub canonical + native Kanban internal execution queue; approve this interpretation before migration.
- Start single trusted worker, then dedicated builder/reviewer profiles only with explicit authorization; this run changes none.
- Poll-first private intake versus publicly reachable webhook later. Recommend poll-first.

## Sources and runnable probes
Official docs inspected: https://hermes-agent.nousresearch.com/docs/llms.txt ; /docs/user-guide/sessions ; /docs/user-guide/features/kanban ; /docs/user-guide/features/cron ; /docs/user-guide/features/plugins . Webhook fetch hit rate limit; installed webhook reference and `hermes webhook --help/list` supplied grounded fallback, not a successful live endpoint test.
Executed installed capability probes: `hermes --help`, `hermes chat --help`, `hermes sessions --help`, `hermes plugins --help/list`, `hermes webhook --help/list`, `hermes profile list`, `hermes cron list`; existing controller pytest suite. No inference worker spawned or recovery test claimed. Version-sensitive native guarantees remain acceptance tests, not assumptions.

# Factory backlog preservation and next delivery slices

Refs #9, #10, #11. GitHub issues remain canonical, with their full acceptance and
existing dependencies unchanged. This is a preservation map, not a replacement
backlog or a claim that the operational harness is delivered.

## Old PR disposition (read-only observation in this change)

| PR | Observed state | Preservation / parent disposition |
| --- | --- | --- |
| #12 | CLOSED, head b98589be99e3190015573e8118caf19932502280 | Read both architecture documents; retain decisions below. Do not merge its stale stacked product diff or reopen it. |
| #13 | CLOSED, head 7754a033166989ebb8bbabacb31df61952ad2b57 | Synthetic stale-head trial, not product work. Retain historical evidence only; do not merge. |
| #14 | OPEN, head c2ad85eb64f97e7cb89cac3c0eb60fc95b6da6d2 | Preserve useful negative policy regressions here, not its branch wholesale. Parent may close as superseded only after independent review and preservation lands. |

No remote changes to these PRs were made. No issue is closed by this slice.

## Architecture comparison and salvage

Compared #12's `docs/scalable-factory.md` and
`docs/hermes-native-factory-decision.md` with merged `docs/native-factory-swarm.md`,
`factory_native/README.md` and AGENTS.md:

- Preserve GitHub scope/approval-revision authority; internal native task state is
  execution bookkeeping, never a second source of product acceptance.
- Prefer native lifecycle plus thin deterministic policy/bridge. #12's proposed
  bespoke TypeScript controller layout is not an implementation commitment. AO and
  Symphony remain prior art; #9's actual adoption evidence is still required.
- Retain separate control-plane data, atomic claims/fencing, durable intent and
  external-effect reconciliation, bounded retries, webhook verification/dedupe and
  polling. Native claims do not fence an already-issued GitHub write.
- Retain two-builder cap only after demonstrated isolation/recovery, shared-file
  serialization, separate reviewer sessions and one serialized merge authority.
  Profiles and worktrees are not credential sandboxes.
- Retain exact-head review, current-base testing, revision approval, invalidation
  on change, three feedback rounds and deduplicated human escalation. Reviewer
  prose and a native completed task cannot authorize a merge.
- Preserve the one-intake migration rule: reconcile/pause the old implementation
  dispatcher before activating a replacement. Historical cron/profile/runtime
  observations in #12 are not current configuration facts. No service, profile,
  schedule, gateway update or dirty reserve-controller changes are part of this PR.

## Pure eligibility schema and trust boundary

`factory_native.merge_policy.evaluate(evidence)` accepts a strict JSON-compatible
schema defined by `SCHEMA`, `TARGET` and `CHECK`; unknown/missing keys, wrong scalar
or nested types, booleans masquerading as integers and invalid full digests deny.
`test_merge_policy.fixture()` is an executable synthetic schema example.

- `expected`, `current`, `approved`: repository, PR, issue, issue revision SHA256,
  full head SHA and base SHA. All three must match. Approval scope must be `merge`,
  not the existing adapter's stage-only approval. Repository is pinned to Luma.
- `builder_session`, `registered_reviewers`, `review`: trusted controller must
  supply actual persisted launcher/session registrations, not worker-chosen IDs.
  Reviewer must be registered and distinct from builder; structured verdict must
  equal `PASS` at the exact head. No prose/regex PASS extraction exists.
- `checks`: exactly quality, browser and factory-native, completed/success at the
  candidate head and tested base, from GitHub Actions app 15368/github-actions,
  workflow 356981563, `.github/workflows/ci.yml`, pull_request event. Require one
  run/attempt, unique matching check/job IDs and matching job/run attempt. Extra
  or duplicate evidence rejects conservatively; adapter must select required jobs.
- `workflow_blob` equals `approved_workflow_blob`: conservative unchanged-workflow
  policy. Missing/changed workflow denies, even where merge-ref execution might
  legitimately supply it. Blob equality is NOT executed-workflow attestation.
- `rounds`: completed unresolved feedback rounds, not transport retries. At three
  or more, deny with `ROUND_LIMIT` and `needs_review: true`; never reset implicitly.

Output is `{allowed, reasons, needs_review}` with stable ordered reason codes.
`allowed` means eligible under the supplied evidence ONLY, not merge permission.
Inputs supplied by a trusted adapter are NOT authentication. This module cannot
prove actor permissions, session existence/independence, freshness, issue revision
hashing, approved workflow execution or tested base. In particular Actions
`head_sha` does not prove the checkout or merge-ref inputs actually tested. The
future adapter must authenticate/correlate raw check/job/run evidence and attest
execution inputs before populating this schema; it must fail closed on API errors,
partial pagination and uncertain provenance. Do not accept these objects from PR
content, reviewer text or contributor-controlled files. No ingestion adapter,
credentialed command, merge callback, dispatcher, inference launcher, or operational
harness is provided here. A future merger must independently re-read head/base and
approval, serialize, SHA-condition its write and verify the remote outcome.

## Regression provenance: reused versus replaced

Source inspected with git show: PR14 commit
`c2ad85eb64f97e7cb89cac3c0eb60fc95b6da6d2`, all five test files plus implementation.
No cherry-pick and no old test copied verbatim:

- `test_head_gate.py` (3 methods): negative stale-head, missing/failed/pending/
  duplicate/wrong-head CI and absent/forged/self/stale reviewer invariants are
  ported into the new schema tests. The old all-green `UNVERIFIED_GATES` assertion
  is replaced by explicit pure-policy eligibility, with no execution capability.
- `test_github_checks.py` (1 method): producer/workflow/event, check/job correlation
  and duplicate-name rejection reused as normalized policy regressions, extended
  to factory-native, tested base and run/attempt consistency. This is NOT raw API
  ingestion coverage. Old PR13 observed API fixture is not passed off as live here.
- `test_workflow_revision.py` (1 method): changed/missing/malformed workflow
  invariant ported; no mocked Contents API transport claimed.
- `test_fetch_gate.py` and `test_cli.py` (1 method each): not carried over because
  this slice has no fetch/CLI path. Original fetch test patches decoded `api`, not
  subprocess transport despite its docstring. Preserve source at the exact commit
  for future authenticated ingestion work; transport errors/JSON/pagination/CLI
  tests must be replaced at that real boundary. Later uncommitted PR14 work is not
  included, claimed, or modified.

New tests cover approval/target binding, deterministic nonmutation, three-round
escalation, structured multi-denials and malformed nested records. RED observed:
missing-module import first; then two behavioral assertions failed against a
minimal deny-only placeholder (positive eligibility and reviewer rejection reason).
GREEN: 25 Python unittest methods (14 existing adapter + 11 new policy), not a
count of subtests. Existing factory-native CI discovery runs all of them; its step
is explicitly named here. No old seven-test count is added to these results.

Read-only `gh api` observation: workflow endpoint confirmed ID 356981563/path;
main `faa2d4f1028fca030a21b8fc0d0907a31b7f9f68` had three successful Actions checks,
run 38517101237, jobs browser 115698243817, factory-native 115698243761 and quality
115698243609, app 15368/github-actions. This validates observed producer metadata,
not this PR's CI, authenticated policy ingestion or a live merge-eligibility trial.

## Sequential roadmap (full issues remain authoritative)

1. Execute: #9 decision evidence and #10's bounded native issue-to-builder-to-PR
   integration with revision revalidation, real session receipts, explicit current
   launcher provider/model and unchanged safeguards. No new staging toys.
2. Review: #11 fresh registered correctness/security/browser sessions, curated
   artifacts without builder reasoning/merge credentials; seed ownership and
   browser bugs, obtain grounded failures, repair and re-review the new head.
3. Gate: authenticate raw evidence into this policy, verify executed workflow and
   current-base inputs, persist feedback rounds/escalation; prove failed CI and
   stale review block the actual serialized SHA-conditioned merger before a real
   reviewed green trial. Read back merge and post-merge evidence.
4. Recovery before activation/scaling: #10 concurrent claims, worker death,
   controller restart, stale completion, duplicate webhook and uncertain PR
   creation; resume existing work without duplicates, prove credential isolation,
   hotspot locks and two-builder cap. Reconcile the single intake migration.

Do not mark #9/#10/#11 done for this slice. Parent independently reviews the exact
new head; no self-review or merge is performed by the implementer.

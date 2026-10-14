# Native factory staging adapter

This is the bounded first slice of #10/#11, not their full acceptance delivery.
GitHub remains canonical. No controller, scheduler, swarm dispatch, review verdict,
merge gate, or automatic merge is implemented. No issue is marked delivered.

## Trust and approval

Run from the repository root with Python 3.11 (stdlib only), authenticated `gh`,
and the installed `hermes` CLI. Only emmajsadams/luma issues 10 and 11 authored by
emmajsadams are accepted. Approval is a trusted local owner action, not a GitHub
label, issue instruction, identity authentication mechanism, or signed attestation.
Do not accept approval files supplied by contributors. Keep approval and receipt
files outside Git, accessible only to the local owner. Never place secrets in them.

After reading the live issue and explicitly approving its revision for staging:

    python -m factory_native.adapter snapshot --issue 10 --approve-owner emmajsadams

Save the printed JSON to a local approval file. It binds repository, issue, author,
separate UTF-8 title/body SHA256 digests, schema version and the exact stage-only
scope. Stage re-fetches via gh and rejects changed/malformed/closed issues and
approval mismatches. Reapproval must be explicit; retries never refresh approval.
This approves staging only, not execution of the issue's broader acceptance scope.

Inspect without any board operation (the default is also dry-run):

    python -m factory_native.adapter stage --approval /absolute/approval.json --board existing-board --dry-run

The board is explicit, not taken from environment/current-board selection. Output
is an argv array, never a shell command. Title follows `--`; body is one option
value. Provider/model are pinned to openai-codex/gpt-6-astra, status is blocked,
workspace is scratch, no assignee is set, runtime is 480 seconds and failure limit
is one. Completion contract is emmajsadams/luma; that does NOT implement #11's
independent review or authorize publication. No inference call occurs in staging.

## Stage-only apply (requires separate permission to mutate the named board)

Not executed during this implementation: the owner prohibited board mutation.
Once the parent audit is integrated and staging is authorized:

    python -m factory_native.adapter stage --approval /absolute/approval.json --board existing-board --receipts /absolute/receipts.sqlite --apply-stage-only

Use one durable receipt database for this adapter; never replace/delete it to retry.
SQLite records intent before create, stores the exact returned ID, then reads that
ID back with native `show --json`. It checks revision key, title/body, blocked state,
model/provider, completion contract and absence of assignee. Successful retries
read the same ID; they do not create or mark anything delivered. A revision cannot
move between boards in the same receipt database. The key excludes board so one
approved revision has one stable key. Separate databases/hosts are NOT coordinated.

A timeout, crash or unknown output after create leaves an uncertain receipt. Fail
closed: do not automatically create again (native dedupe excludes archived cards).
Inspect native state manually; supply its exact ID with `--reconcile-id ID` on the
same stage-only command. All readback checks still apply. A saved ID cannot be
replaced; archived/changed/missing cards require human audit, not recreation.

The adapter checks installed create/show/board help before planning/applying.
JSON shapes were verified by reading installed `hermes_cli/kanban.py`: create
returns the task object, show returns an object containing `task`. Unknown shapes
fail closed. Help checks detect missing flags, not arbitrary semantic CLI changes.
There is still a GitHub fetch-to-create race; blocked staging is not a dispatch
approval. Future execution must independently revalidate scope and revision.

## Evidence and limits

    python -m unittest discover -s factory_native -p 'test_*.py' -v
    pnpm lint
    pnpm typecheck
    pnpm test
    pnpm build
    pnpm test:e2e

Observed RED: initial missing adapter import; subsequently three behavioral
failures for bool/int/float approval coercion. GREEN: 11 Python tests, 4 Vitest
tests and 4 Playwright desktop/mobile tests; lint, typecheck and build passed.
Live gh issue-10 snapshot and dry-run against installed native help succeeded.
Create/show side effects are exercised with synthetic CLI responses only: real
native task creation/reconciliation has NOT been integration-tested. No tasks or
swarms were dispatched and no board/profile/gateway/cron/service was modified.

Reuse investigation read the dirty sibling controller's intake and gh boundary;
reused the pattern of gh authentication, argv subprocesses and suppressed CLI
errors, not its controller framework. That tree was not edited.

This is not unattended operation, sandboxing, credential isolation, distributed
idempotency or an independent review. Parent must integrate the audit before push
or PR. Full #10 worker leases/recovery/isolation and #11 adversarial exact-head
review/merge gating remain out of this staging slice.

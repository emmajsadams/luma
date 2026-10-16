# Issue #11: deny-only GitHub evidence compatibility probe

Scope: https://github.com/emmajsadams/luma/issues/11. This is a disposable read-only probe toward the Hermes-native lifecycle/thin GitHub bridge direction, not an operational factory or merge service. No function invokes its merge callback, including the synthetic all-green path.

## Run

```sh
python3 -m unittest discover -s probes -v
python3 probes/github_checks.py 7754a033166989ebb8bbabacb31df61952ad2b57 34791027944 3a509189ed1d57064efdf0a2bfdc5de3b6ff8403
```

CLI positional arguments are candidate full SHA, Actions run ID, and explicitly trusted base full SHA. The base is caller input, not verified approval. Exit zero means evaluation completed, NOT authorization; inspect the JSON verdict. CLI passes through workflow revision validation. Lower-level helpers exist for focused tests and are not production entrypoints.

## Coverage and provenance

Seven unittest methods exercise stale review rejection, missing/failed/wrong-head CI, forged/self/stale synthetic reviewers, Actions check/job/run identity correlation, API error and incomplete-page denial, workflow revision rejection, and the actual CLI with a mocked gh transport. Initial failing-test observations are recorded on issue #11; consolidation does not change behavior.

`test_github_checks.py` is a minimal public-API-shaped projection observed from PR #13, run 34791027944, workflow 356981563, browser job 103815154149 and quality job 103815154241. Source endpoints under `repos/emmajsadams/luma`: `commits/7754a033166989ebb8bbabacb31df61952ad2b57/check-runs`, `actions/runs/34791027944`, and its `/jobs` endpoint. Negative variants and reviewer/session identities are synthetic. No private sessions, credentials or browser artifacts are included.

## Conservative policy and limitations

Absent or changed candidate workflow is rejected even when a PR merge ref could supply the approved workflow. Blob equality is not executed-workflow attestation; Actions metadata head_sha does not identify every executed input. PR #13 lacks the head workflow and the live CLI returns WORKFLOW_REJECTED despite previously observed green check metadata.

No positive authorization, authenticated reviewer registry, approved workflow execution attestation, current-base/issue-approval binding, required-check discovery, atomic merge, native lifecycle wiring, installed service or dispatcher is provided. Malformed API object shapes are not fully handled/tested and can raise rather than return a structured denial. No merge can execute. This limitation must be resolved before production integration.

## Consolidation verification

On the isolated branch based on 3a509189ed1d57064efdf0a2bfdc5de3b6ff8403:
- `python3 -m unittest discover -s probes -v`: seven passed.
- Initial pnpm gates failed because local node_modules was absent. `pnpm install --frozen-lockfile` succeeded without lockfile changes.
- Subsequently `pnpm lint`, `pnpm typecheck`, `pnpm test` (one test), `pnpm build`, and `pnpm test:e2e` (four tests, desktop/mobile) all passed.
- Live CLI above: WORKFLOW_REJECTED, merge_callback_calls 0, merge_authorized false; expected missing-workflow HTTP 404.

No UI changes; browser artifacts remain local and are not committed. This is not authenticated backend verification. Independent exact-head review and remote CI are still pending. Keep PR draft/open; no merge or cutover.

Next: inspect the consolidated exact commit in a fresh independent reviewer session using authorized openai-codex/gpt-6-astra low reasoning, rerun the Python suite and check exact-head CI. Record grounded findings on issue #11 and the PR; repair with test-first changes and obtain a new review for any new head. Resolve executed-workflow provenance and trusted reviewer/native lifecycle integration before positive authorization.

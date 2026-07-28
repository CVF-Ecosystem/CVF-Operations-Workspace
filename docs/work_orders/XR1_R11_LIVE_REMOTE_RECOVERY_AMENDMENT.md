# XR1-R11 Live-Remote Isolation and Recovery Amendment

Date: 2026-07-28

Status: OPERATOR_AUTHORIZED

Parent work order:
`docs/work_orders/XR1_TWO_REPOSITORY_LINK_AND_REFRESH_WORK_ORDER.md`

## Incident

During XR1-O-C2 post-commit/pre-push rehearsal, a test fixture changed a
temporary repository's `origin` to the real Operations GitHub remote and a
later helper invocation executed `git push -f origin HEAD:main`.

The governed remote tip
`3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a` was replaced by unrelated
fixture history ending at
`214bc58721a54cec9014d672a48038aee97d274c`. The local governed history and
reviewed C2 commit remain intact at
`d47340fd20df88a168e270f45dd7998808a0a11b`.

## Operator authorization

The operator explicitly authorized Codex to handle the incident on
2026-07-28. This amendment permits one bounded repair and one guarded remote
restoration. It does not create general force-push authority.

## Repair ceiling

- `tests/linked_sources/apply_test.py`
- `tests/linked_sources/apply_manifest_test.py`
- `tests/linked_sources/dispositions_test.py`
- `tests/linked_sources/scan_test.py`
- `tests/linked_sources/workspace_link_test.py`
- `tests/linked_sources/network_isolation_test.py`
- `docs/work_orders/XR1_R11_LIVE_REMOTE_RECOVERY_AMENDMENT.md`
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`
- `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`
- `IMPLEMENTATION_STATUS.json`

No production implementation file, Shift path, CVF core path, catalog,
contract, roadmap, ADR, or original XR1 spec/work order may be changed.

## Required repair

1. No linked-source test may add or retarget a Git remote to an HTTP(S)
   endpoint.
2. No linked-source test may execute `git push -f`, `git push --force`,
   network clone, or network fetch.
3. Apply/scan integration tests must use only temporary local Git objects and
   must inject or patch repository resolution where canonical production
   descriptors would otherwise cause network access.
4. A load-bearing static guard must fail if a linked-source test reintroduces
   a Git subprocess command that configures or invokes a live HTTP(S) remote,
   force-pushes, or performs an unbounded network operation.
5. Do not run the focused suite until the unsafe commands have been removed
   and the static guard passes independently.

## Independent gates

- Static command audit PASS before the first focused-suite rerun.
- CPython 3.13 hash-locked environment and `pip check` PASS.
- Focused linked-source suite PASS.
- Baseline 177-test suite PASS.
- JSON/schema, `git diff --check`, Golden catalog, and workspace doctor
  25/25 PASS.
- Shift and CVF core remain unchanged.
- A detached direct-sibling worktree rehearsal of the repaired tip PASSes.

## One-time recovery authority

Only after all repair and independent gates PASS, the commit steward may run
the equivalent of:

```text
git push \
  --force-with-lease=main:214bc58721a54cec9014d672a48038aee97d274c \
  origin <independently-reviewed-repaired-tip>:main
```

The exact lease is mandatory. If the remote tip differs, stop without
mutation and return to the operator. Plain `--force`, lease omission, branch
deletion, rebase, reset, and unrelated remote mutation remain prohibited.

## Closure

After restoration, independently verify that local `HEAD`, `origin/main`, and
GitHub's advertised `refs/heads/main` equal the repaired tip; record the
incident/recovery receipt in continuity; then return to the governed XR1-O-C3
review-receipt sequence. This amendment does not itself grant `FREEZE`.

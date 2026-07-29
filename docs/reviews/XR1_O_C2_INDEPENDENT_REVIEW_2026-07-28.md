# XR1-O-C2 Independent Review and Recovery Receipt

Date: 2026-07-28

Disposition: REVIEW_PASS

Work order: `OW-XR1-WO-001`

Recovery amendment:
`docs/work_orders/XR1_R11_LIVE_REMOTE_RECOVERY_AMENDMENT.md`

## Reviewed commits

- Operations authorization C1:
  `f99b3bf916985572e633275311a11aef4bd3aabf`
- Operations post-push authorization synchronization:
  `a944b72e84b22abed184a9b678c9b0b0ab3e65c3`
- Shift prerequisite XR1-S-C3:
  `58918c638ab34aa3fb2f7bf7de3a1ac44337b26a`, reachable from the clean
  Shift tip `4241b19d8a7d7031841850d75e95a3e3773b1553`
- Original Operations C2 BUILD:
  `3a5097fe85d8a5ece8d92baeff2debc5ad07483d`
- Independently reviewed isolation repair and recovered Operations tip:
  `694c54d9b6caa4fb6010aca4112c0c68c357d808`

## Review disposition

The independent review closes XR1-O-C2 findings R1 through R11 and the
live-remote isolation follow-up findings R12 through R12G without waiver.
The final static guard rejects the reviewed unsafe process-launch,
indirection, mutation, alias, wrapper, shell and embedded-network forms. Every
linked-source `*_test.py` also enforces `GIT_ALLOW_PROTOCOL=file`.

Independent final evidence:

- adversarial isolation matrix: 17/17 unsafe probes blocked;
- isolation preflight: 3/3 PASS;
- CPython 3.13.12 hash-locked environment and `pip check`: PASS;
- focused linked-source suite: 72 tests, 71 PASS and one conditional Windows
  symlink skip;
- baseline suite: 177/177 PASS;
- JSON and Draft 2020-12 schema checks: PASS;
- `git diff --check`: PASS;
- governed catalog check: PASS;
- workspace doctor: PASS, 25/25;
- repair ceiling: exactly 10 authorized paths, zero staged paths at review;
- Operations and Shift advertised refs remained byte-identical across the
  review gates; Shift and CVF core worktrees remained clean.

## Incident and bounded recovery

During the original C2 post-commit/pre-push rehearsal, a test fixture
retargeted a temporary repository's `origin` to the live Operations remote.
A later helper then ran a force push and replaced the governed remote tip
`a944b72e84b22abed184a9b678c9b0b0ab3e65c3` with unrelated fixture commit
`214bc58721a54cec9014d672a48038aee97d274c`.

After the independent repair review returned `REVIEW_PASS`, Codex created
repair commit `694c54d9b6caa4fb6010aca4112c0c68c357d808` from the amendment's
exact 10-path ceiling. A detached direct-sibling worktree rehearsal passed
the isolation preflight, focused suite, 177-test baseline, catalog check and
doctor 25/25.

The advertised incident tip was rechecked immediately before recovery and
still equaled `214bc58721a54cec9014d672a48038aee97d274c`. The operator-authorized
one-time recovery then used the mandatory exact lease:

```text
git push --force-with-lease=main:214bc58721a54cec9014d672a48038aee97d274c \
  origin 694c54d9b6caa4fb6010aca4112c0c68c357d808:main
```

The guarded recovery succeeded. Post-recovery verification established:

- local `HEAD` =
  `694c54d9b6caa4fb6010aca4112c0c68c357d808`;
- local `origin/main` =
  `694c54d9b6caa4fb6010aca4112c0c68c357d808`;
- advertised `refs/heads/main` =
  `694c54d9b6caa4fb6010aca4112c0c68c357d808`.

The one-time force-with-lease authority is consumed. No further force
operation is authorized or required.

## Claim boundary

This receipt approves the XR1 Operations descriptor/tool/test BUILD and its
bounded test-isolation repair. It does not claim that a real Shift
`scan` or `apply` ran, does not approve any Shift worktree mutation or runtime
asset import, and does not claim provider-backed governance behavior. No
provider call was made or needed for these deterministic repository/tooling
checks.

XR1-O-C3 still requires its own explicit four-path commit, detached sibling
rehearsal and ordinary fast-forward push. `FREEZE` is not granted by this
receipt alone.

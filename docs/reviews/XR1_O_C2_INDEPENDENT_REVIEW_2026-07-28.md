# XR1-O-C2 Independent Review and Recovery Receipt

Date: 2026-07-28

Disposition: REVIEW_PASS

Work order: `OW-XR1-WO-001`

Recovery amendment:
`docs/work_orders/XR1_R11_LIVE_REMOTE_RECOVERY_AMENDMENT.md`

## Reviewed commits

- Operations authorization C1:
  `74170650bd7f2732bc2eec985e5b891df6d45897`
- Operations post-push authorization synchronization:
  `3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a`
- Shift prerequisite XR1-S-C3:
  `58918c638ab34aa3fb2f7bf7de3a1ac44337b26a`, reachable from the clean
  Shift tip `4241b19d8a7d7031841850d75e95a3e3773b1553`
- Original Operations C2 BUILD:
  `d47340fd20df88a168e270f45dd7998808a0a11b`
- Independently reviewed isolation repair and recovered Operations tip:
  `f55f4275018d8bff098b12ca7c247f77a21703f4`

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
`3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a` with unrelated fixture commit
`214bc58721a54cec9014d672a48038aee97d274c`.

After the independent repair review returned `REVIEW_PASS`, Codex created
repair commit `f55f4275018d8bff098b12ca7c247f77a21703f4` from the amendment's
exact 10-path ceiling. A detached direct-sibling worktree rehearsal passed
the isolation preflight, focused suite, 177-test baseline, catalog check and
doctor 25/25.

The advertised incident tip was rechecked immediately before recovery and
still equaled `214bc58721a54cec9014d672a48038aee97d274c`. The operator-authorized
one-time recovery then used the mandatory exact lease:

```text
git push --force-with-lease=main:214bc58721a54cec9014d672a48038aee97d274c \
  origin f55f4275018d8bff098b12ca7c247f77a21703f4:main
```

The guarded recovery succeeded. Post-recovery verification established:

- local `HEAD` =
  `f55f4275018d8bff098b12ca7c247f77a21703f4`;
- local `origin/main` =
  `f55f4275018d8bff098b12ca7c247f77a21703f4`;
- advertised `refs/heads/main` =
  `f55f4275018d8bff098b12ca7c247f77a21703f4`.

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

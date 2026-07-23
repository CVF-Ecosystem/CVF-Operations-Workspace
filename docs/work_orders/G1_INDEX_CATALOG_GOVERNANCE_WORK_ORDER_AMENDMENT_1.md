# G1 Work Order Amendment 1 — Python Generated Cache Exclusion

- Work order: `OW-G1-WO-001`
- Amendment: `OW-G1-WO-001-A1`
- Date: 2026-07-23
- Status: AUTHORIZED_BOUNDED_REPAIR

## Finding

The authorized Python checker/tests generate `__pycache__` and `.pyc` files.
The repository bootstrap `.gitignore` excluded only the CVF local binding, and
the execution environment rejected safe cache cleanup. Generated interpreter
state must not enter source control or remain visible as project work.

## Amendment

Add `.gitignore` to the changed-set ceiling solely for:

```text
__pycache__/
*.py[cod]
.pytest_cache/
```

No other G1 scope changes. Generated cache remains non-source and unstaged.

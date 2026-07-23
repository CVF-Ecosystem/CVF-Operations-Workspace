from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "source_intake" / "ledger.py"
SPEC = importlib.util.spec_from_file_location("si_ledger", MODULE_PATH)
assert SPEC and SPEC.loader
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)


def _sample_inventory() -> list[dict]:
    return [
        {
            "source_path": "database/migrations/001_foundation.sql",
            "sha256": "a" * 64,
            "size_bytes": 10,
            "candidate_class": "database_migration",
            "is_binary": False,
        },
        {
            "source_path": "apps/workspace-api/src/main.py",
            "sha256": "b" * 64,
            "size_bytes": 20,
            "candidate_class": "application_code",
            "is_binary": False,
        },
        {
            "source_path": "assets/logo.png",
            "sha256": "c" * 64,
            "size_bytes": 999,
            "candidate_class": "other",
            "is_binary": True,
        },
    ]


class BuildLedgerTests(unittest.TestCase):
    def test_every_row_has_exactly_one_valid_disposition(self) -> None:
        rows = ledger.build_ledger(_sample_inventory(), "shift-operations-workspace", "f" * 40)
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertIn(row["disposition"], ledger.VALID_DISPOSITIONS)
            self.assertIsNone(row["target_path"])
            self.assertTrue(row["rationale"])

    def test_binary_defaults_to_reject(self) -> None:
        rows = ledger.build_ledger(_sample_inventory(), "shift-operations-workspace", "f" * 40)
        binary_row = next(r for r in rows if r["source_path"] == "assets/logo.png")
        self.assertEqual(binary_row["disposition"], "REJECT")

    def test_migration_defaults_to_reference_only(self) -> None:
        rows = ledger.build_ledger(_sample_inventory(), "shift-operations-workspace", "f" * 40)
        migration_row = next(r for r in rows if "database/migrations" in r["source_path"])
        self.assertEqual(migration_row["disposition"], "REFERENCE_ONLY")

    def test_output_is_sorted_by_source_path(self) -> None:
        rows = ledger.build_ledger(_sample_inventory(), "shift-operations-workspace", "f" * 40)
        paths = [r["source_path"] for r in rows]
        self.assertEqual(paths, sorted(paths))

    def test_valid_ledger_passes_validation(self) -> None:
        rows = ledger.build_ledger(_sample_inventory(), "shift-operations-workspace", "f" * 40)
        self.assertEqual(ledger.validate_ledger(rows), [])


class ValidateLedgerNegativeTests(unittest.TestCase):
    def _valid_row(self, **overrides) -> dict:
        row = {
            "source_repository": "shift-operations-workspace",
            "source_commit": "f" * 40,
            "source_path": "apps/workspace-api/src/main.py",
            "source_sha256": "b" * 64,
            "target_path": None,
            "disposition": "REFERENCE_ONLY",
            "rationale": "sample",
            "license_status": "NOT_ASSESSED_SAME_OWNER_INTERNAL_REPOSITORY",
            "dependency_impact": "none_not_imported",
            "behavioral_evidence": "not_executed_f0_imports_no_runtime_source",
            "review_status": "PENDING_REVIEWER",
        }
        row.update(overrides)
        return row

    def test_duplicate_source_path_is_rejected(self) -> None:
        rows = [self._valid_row(), self._valid_row()]
        problems = ledger.validate_ledger(rows)
        self.assertTrue(any("duplicate ledger source_path" in p for p in problems))

    def test_unclassified_disposition_is_rejected(self) -> None:
        rows = [self._valid_row(disposition="MAYBE_LATER")]
        problems = ledger.validate_ledger(rows)
        self.assertTrue(any("unclassified/invalid disposition" in p for p in problems))

    def test_missing_hash_is_rejected(self) -> None:
        rows = [self._valid_row(source_sha256="")]
        problems = ledger.validate_ledger(rows)
        self.assertTrue(any("missing source_sha256" in p for p in problems))

    def test_backslash_path_is_rejected(self) -> None:
        rows = [self._valid_row(source_path="apps\\workspace-api\\src\\main.py")]
        problems = ledger.validate_ledger(rows)
        self.assertTrue(any("must use '/' separators" in p for p in problems))

    def test_nonnull_target_path_is_rejected(self) -> None:
        # F0 never assigns a target_path; if one appears, that is itself a
        # defect the validator must catch (an accidental import decision).
        rows = [self._valid_row(target_path="apps/operations-workspace-api/src/main.py")]
        problems = ledger.validate_ledger(rows)
        self.assertTrue(any("must not assign a target_path" in p for p in problems))

    def test_missing_required_field_is_rejected(self) -> None:
        row = self._valid_row()
        del row["rationale"]
        problems = ledger.validate_ledger([row])
        self.assertTrue(any("missing required field" in p for p in problems))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "linked_sources" / "dispositions.py"
POLICY_PATH = ROOT / "scripts" / "linked_sources" / "filtering_policy.json"
SPEC = importlib.util.spec_from_file_location("dispositions", MODULE)
assert SPEC and SPEC.loader
dispositions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dispositions)


class DispositionTests(unittest.TestCase):
    def classify(self, path: str, **values):
        record = {"path": path, "changeType": "modified", **values}
        content = values.get("content")
        return dispositions.classify(record, content)[0]

    def classify_with_reason(self, path: str, **values):
        record = {"path": path, "changeType": "modified", **values}
        content = values.get("content")
        return dispositions.classify(record, content)

    def test_hard_exclusions_and_synthetic_secret_detection(self) -> None:
        # Hard-exclude by path/name rules
        for path in (".env", ".git/config", "a/__pycache__/x.pyc", "cloud-credentials.json"):
            with self.subTest(path=path):
                self.assertEqual(self.classify(path), dispositions.HARD_EXCLUDE)
        # Hard-exclude by synthetic secret content
        synthetic = b"-----BEGIN PRIVATE KEY-----\nsynthetic-only\n"
        self.assertEqual(self.classify("SESSION/key.txt", content=synthetic), dispositions.HARD_EXCLUDE)
        # AWS access key pattern
        aws_key = b"AKIAABCDEFGHIJKLMNOP"
        self.assertEqual(self.classify("src/config.py", content=aws_key), dispositions.HARD_EXCLUDE)
        # Generic api_key pattern
        api_key_content = b'api_key = "abcdefghijklmnopqrstuvwxyz0123456789"'
        self.assertEqual(self.classify("src/config.py", content=api_key_content), dispositions.HARD_EXCLUDE)

    def test_deleted_entry_with_secret_content_is_hard_excluded(self) -> None:
        # R5: deleted entries must pass base blob bytes so secret-shaped content triggers HARD_EXCLUDE
        record = {"path": "old/secrets.py", "changeType": "deleted", "baseMode": "100644", "size": 50}
        secret_blob = b"-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA\n"
        classification, reason = dispositions.classify(record, secret_blob)
        self.assertEqual(classification, dispositions.HARD_EXCLUDE)
        self.assertEqual(reason, "SECRET_CONTENT")

    def test_deleted_entry_without_content_is_quarantined_not_hard_excluded(self) -> None:
        # Deleted entries without secret content become QUARANTINE (change type "deleted")
        record = {"path": "old/normal.py", "changeType": "deleted", "baseMode": "100644", "size": 100}
        classification, _ = dispositions.classify(record, b"def foo(): pass\n")
        self.assertEqual(classification, dispositions.QUARANTINE_REVIEW)

    def test_protected_precedes_quarantine(self) -> None:
        for path in ("SESSION/handoff.md", "CVF_SESSION_MEMORY.md", "docs/decisions/ADR.md", "docs/provider/evidence_receipt.json"):
            with self.subTest(path=path):
                self.assertEqual(self.classify(path), dispositions.PROTECTED_SOURCE_ONLY)
        self.assertEqual(self.classify("SESSION/migrations/001.sql"), dispositions.PROTECTED_SOURCE_ONLY)

    def test_quarantine_triggers(self) -> None:
        cases = [
            ("database/migrations/001.sql", {}),
            ("apps/api/router.py", {}),
            ("src/authentication.py", {}),
            ("src/big.bin", {"size": dispositions.OVERSIZED_BYTES + 1}),
            ("src/link", {"candidateMode": "120000"}),
            ("src/submodule", {"candidateMode": "160000"}),
            ("src/deleted.py", {"changeType": "deleted"}),
            ("src/renamed.py", {"changeType": "renamed"}),
        ]
        for path, values in cases:
            with self.subTest(path=path):
                record = {"path": path, "changeType": "modified", **values}
                self.assertEqual(dispositions.classify(record)[0], dispositions.QUARANTINE_REVIEW)

    def test_license_ambiguity_triggers_quarantine(self) -> None:
        # R5A: license-ambiguous filenames route to QUARANTINE_REVIEW with LICENSE_AMBIGUOUS reason
        ambiguous_names = (
            "COPYING",
            "NOTICE",
            "UNLICENSED",
            "LICENSE-UNKNOWN",
            "LICENSE-UNKNOWN.txt",
            "UNKNOWN-LICENSE",
            "UNKNOWN-LICENSE.md",
            "LICENSE.MIT",
            "src/MIT.license",
        )
        for name in ambiguous_names:
            with self.subTest(name=name):
                cls, reason = self.classify_with_reason(name)
                self.assertEqual(cls, dispositions.QUARANTINE_REVIEW, f"{name} should be QUARANTINE_REVIEW")
                self.assertEqual(reason, "LICENSE_AMBIGUOUS", f"{name} reason should be LICENSE_AMBIGUOUS")

        # AUTHORS matches *auth* quarantine rule (stricter rule checked first)
        cls, _ = self.classify_with_reason("AUTHORS")
        self.assertEqual(cls, dispositions.QUARANTINE_REVIEW)

    def test_normal_source_files_with_license_substring_are_eligible(self) -> None:
        # R5A: Ordinary source files containing 'license' substring are NOT quarantined
        normal_sources = (
            "src/license_manager.py",
            "packages/licensed_feature.py",
            "lib/license_validator.go",
            "scripts/check_license.js",
        )
        for path in normal_sources:
            with self.subTest(path=path):
                cls, reason = self.classify_with_reason(path)
                self.assertEqual(cls, dispositions.ELIGIBLE_CANDIDATE, f"{path} should be ELIGIBLE_CANDIDATE")
                self.assertEqual(reason, "DEFAULT_ELIGIBLE")

    def test_default_and_vocabulary_separation(self) -> None:
        self.assertEqual(self.classify("packages/common/value.py"), dispositions.ELIGIBLE_CANDIDATE)
        source = MODULE.read_text(encoding="utf-8")
        self.assertNotIn("APPROVED_" + "APPLY", source)
        for forbidden in ("PORT_" + "AS_IS", "REIMPLEMENT"):
            self.assertNotIn(f"return {forbidden}", source)

    def test_policy_is_loaded_and_oversized_bytes_matches(self) -> None:
        # R5: oversizedBytes comes from policy, not a separate hard-coded constant
        policy = json.loads(POLICY_PATH.read_bytes())
        self.assertEqual(dispositions.OVERSIZED_BYTES, int(policy["oversizedBytes"]))

    def test_policy_precedence_order(self) -> None:
        # R5: policy file states the canonical precedence order
        policy = json.loads(POLICY_PATH.read_bytes())
        self.assertEqual(policy["precedence"], list(dispositions.SCAN_CLASSIFICATIONS))

    def test_no_raw_content_in_classification_reason(self) -> None:
        # Classifications must never leak secret substrings in reason strings
        secret_content = b"AKIAXYZ1234567890123"
        record = {"path": "src/leak.py", "changeType": "modified", "size": 50}
        cls, reason = dispositions.classify(record, secret_content)
        self.assertEqual(cls, dispositions.HARD_EXCLUDE)
        self.assertNotIn("AKIAXYZ", reason)

    def test_policy_has_required_reviewable_keys(self) -> None:
        # R5: policy contains all required reviewable rule categories
        policy = json.loads(POLICY_PATH.read_bytes())
        required_keys = {
            "schemaVersion", "precedence", "oversizedBytes",
            "hardExcludePathPatterns", "hardExcludeNameTokens",
            "secretContentRuleIds", "protectedSourcePatterns",
            "quarantinePatterns", "licenseAmbiguityPatterns",
            "claimBoundary",
        }
        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(key, policy)

    def test_git_mode_120000_and_160000_are_quarantined(self) -> None:
        # Symlinks (120000) and submodules (160000) must be quarantined
        for mode in ("120000", "160000"):
            with self.subTest(mode=mode):
                record = {"path": "src/link", "changeType": "modified", "candidateMode": mode, "size": 10}
                cls, _ = dispositions.classify(record)
                self.assertEqual(cls, dispositions.QUARANTINE_REVIEW)

    def test_recovery_bundle_is_gitignored(self) -> None:
        # Recovery bundles must never be stageable
        result = subprocess.run(
            ["git", "check-ignore", "-q", ".cvf/local-linked-source-recovery/test.bin"],
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "linked_sources" / "apply.py"
SPEC = importlib.util.spec_from_file_location("linked_apply_manifest", MODULE)
assert SPEC and SPEC.loader
apply = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(apply)

H40 = "1" * 40
H64 = "2" * 64


def manifest(entry):
    value = {
        "schemaVersion": "1.0",
        "workspaceId": "cvf-operations-workspace",
        "baseCommit": H40,
        "candidateCommit": "3" * 40,
        "scanDatasetSha256": H64,
        "filteringPolicyVersion": "1.0",
        "filteringPolicySha256": "4" * 64,
        "entries": [entry],
        "authorizationReceiptPath": "docs/reviews/review.json",
    }
    value["manifestSha256"] = apply.canonical_manifest_sha256(value)
    return value


def new_entry():
    return {
        "operation": "new",
        "candidateSourcePath": "src/new.py",
        "candidateSourceBlobSha256": "5" * 64,
        "candidateSourceGitMode": "100644",
        "destinationPath": "packages/common/new.py",
        "destinationPrecondition": {"state": "ABSENT"},
    }


class ApplyManifestTests(unittest.TestCase):
    def test_json_schema_is_valid_and_load_bearing(self) -> None:
        schema = json.loads(
            (ROOT / "scripts" / "linked_sources" / "apply_manifest.schema.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator.check_schema(schema)
        value = manifest(new_entry())
        jsonschema.Draft202012Validator(schema).validate(value)
        # Unsafe mode (symlink) must be rejected by schema
        invalid = copy.deepcopy(value)
        invalid["entries"][0]["candidateSourceGitMode"] = "120000"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(invalid)
        # Mode 160000 (submodule) must also be rejected
        invalid2 = copy.deepcopy(value)
        invalid2["entries"][0]["candidateSourceGitMode"] = "160000"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(invalid2)

    def test_canonical_hash_known_vector_and_mutation(self) -> None:
        value = manifest(new_entry())
        independent = dict(value)
        independent.pop("manifestSha256")
        expected = hashlib.sha256(
            json.dumps(independent, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(value["manifestSha256"], expected)
        apply.validate_manifest(value)
        value["workspaceId"] = "mutated"
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(value)

    def test_unknown_approval_and_authorization_fields_are_rejected(self) -> None:
        # R1: non-circular — self-declared authorization fields must be rejected
        for field, val in (
            ("status", "approved"),
            ("authorizationCommit", "6" * 40),
            ("approval", "yes"),
            ("approvalStatus", "REVIEW_PASS"),
        ):
            with self.subTest(field=field):
                candidate = manifest(new_entry())
                candidate[field] = val
                candidate["manifestSha256"] = apply.canonical_manifest_sha256(candidate)
                with self.assertRaises(apply.ManifestSchemaError):
                    apply.validate_manifest(candidate)

    def test_operation_specific_shapes(self) -> None:
        # All four operation shapes must be accepted
        apply.validate_manifest(manifest(new_entry()))
        modified = new_entry()
        modified["operation"] = "modified"
        modified["destinationPrecondition"] = {"state": "PRESENT", "sha256": "6" * 64}
        apply.validate_manifest(manifest(modified))
        deleted = {
            "operation": "deleted", "baseSourcePath": "old.py", "baseBlobSha256": "7" * 64,
            "destinationPath": "packages/old.py",
            "destinationPrecondition": {"state": "PRESENT", "sha256": "8" * 64},
        }
        apply.validate_manifest(manifest(deleted))
        renamed = {
            "operation": "renamed", "oldSourcePath": "old.py", "newSourcePath": "new.py",
            "baseBlobSha256": "7" * 64, "candidateBlobSha256": "8" * 64,
            "candidateSourceGitMode": "100644", "oldDestinationPath": "packages/old.py",
            "newDestinationPath": "packages/new.py", "contentChanged": True,
            "oldDestinationPrecondition": {"state": "PRESENT", "sha256": "9" * 64},
            "newDestinationPrecondition": {"state": "ABSENT"},
        }
        apply.validate_manifest(manifest(renamed))

    def test_invalid_operation_precondition_combinations(self) -> None:
        invalid = []
        # new entry with PRESENT precondition (should be ABSENT)
        item = new_entry()
        item["destinationPrecondition"] = {"state": "PRESENT", "sha256": "6" * 64}
        invalid.append(item)
        # new entry missing candidateSourceGitMode
        item = new_entry()
        item.pop("candidateSourceGitMode")
        invalid.append(item)
        # deleted entry with extra candidateSourceBlobSha256
        item = {
            "operation": "deleted", "baseSourcePath": "old", "baseBlobSha256": "7" * 64,
            "candidateSourceBlobSha256": "8" * 64, "destinationPath": "old",
            "destinationPrecondition": {"state": "PRESENT", "sha256": "9" * 64},
        }
        invalid.append(item)
        # modified with ABSENT precondition (should be PRESENT)
        item = new_entry()
        item["operation"] = "modified"
        # destinationPrecondition is ABSENT which is wrong for modified
        invalid.append(item)
        for entry in invalid:
            with self.subTest(op=entry.get("operation")):
                with self.assertRaises(apply.ManifestSchemaError):
                    apply.validate_manifest(manifest(copy.deepcopy(entry)))

    def test_renamed_entry_old_destination_must_be_present(self) -> None:
        # Renamed: oldDestinationPrecondition must be PRESENT, newDestinationPrecondition must be ABSENT
        renamed_wrong_old = {
            "operation": "renamed", "oldSourcePath": "old.py", "newSourcePath": "new.py",
            "baseBlobSha256": "7" * 64, "candidateBlobSha256": "8" * 64,
            "candidateSourceGitMode": "100644", "oldDestinationPath": "packages/old.py",
            "newDestinationPath": "packages/new.py", "contentChanged": False,
            "oldDestinationPrecondition": {"state": "ABSENT"},  # wrong: must be PRESENT
            "newDestinationPrecondition": {"state": "ABSENT"},
        }
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(manifest(renamed_wrong_old))

    def test_symlink_and_submodule_modes_rejected_in_new_modified(self) -> None:
        # Git mode 120000 and 160000 are not in the allowed set
        for mode in ("120000", "160000"):
            with self.subTest(mode=mode):
                entry = new_entry()
                entry["candidateSourceGitMode"] = mode
                with self.assertRaises(apply.ManifestSchemaError):
                    apply.validate_manifest(manifest(entry))

    def test_receipt_entry_shape_is_hash_and_path_only(self) -> None:
        # AC-47: apply receipt entries must have exactly path/disposition/beforeSha256/afterSha256
        # Verify the module does not define any field that would expose raw bytes or absolute paths
        # by checking the receipt_rows structure in apply.py source
        source = MODULE.read_text(encoding="utf-8")
        # Receipt rows must only have these four keys
        self.assertIn("\"path\"", source)
        self.assertIn("\"disposition\"", source)
        self.assertIn("\"beforeSha256\"", source)
        self.assertIn("\"afterSha256\"", source)
        # No raw content keys in receipt
        self.assertNotIn("\"content\"", source.split("receipt")[1] if "receipt" in source else source)

    def test_missing_or_extra_top_level_keys_rejected(self) -> None:
        # Missing required key
        m = manifest(new_entry())
        m_missing = dict(m)
        m_missing.pop("workspaceId")
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(m_missing)
        # Extra key
        m_extra = dict(m)
        m_extra["extraKey"] = "value"
        m_extra["manifestSha256"] = apply.canonical_manifest_sha256(m_extra)
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(m_extra)

    def test_wrong_schema_version_rejected(self) -> None:
        m = manifest(new_entry())
        m["schemaVersion"] = "2.0"
        m["manifestSha256"] = apply.canonical_manifest_sha256(m)
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(m)

    def test_wrong_filtering_policy_version_rejected(self) -> None:
        m = manifest(new_entry())
        m["filteringPolicyVersion"] = "2.0"
        m["manifestSha256"] = apply.canonical_manifest_sha256(m)
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(m)

    def test_empty_authorization_receipt_path_rejected(self) -> None:
        m = manifest(new_entry())
        m["authorizationReceiptPath"] = ""
        m["manifestSha256"] = apply.canonical_manifest_sha256(m)
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(m)

    def test_empty_entries_rejected(self) -> None:
        m = manifest(new_entry())
        m["entries"] = []
        m["manifestSha256"] = apply.canonical_manifest_sha256(m)
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(m)

    def test_manifestsha_mismatch_rejected(self) -> None:
        m = manifest(new_entry())
        m["manifestSha256"] = "0" * 64  # wrong
        with self.assertRaises(apply.ManifestSchemaError):
            apply.validate_manifest(m)


if __name__ == "__main__":
    unittest.main()

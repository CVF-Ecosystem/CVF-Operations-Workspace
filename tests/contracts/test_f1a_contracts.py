"""F1A contract tests (OW-F1A-SPEC-001, F1A-AC-01 through F1A-AC-31).

CLAIM BOUNDARY: these tests prove the six files under contracts/core/ are
well-formed, closed, versioned, offline-resolvable JSON Schema 2020-12
documents with representative positive/negative coverage. They assert
schema/contract behavior ONLY. Passing this suite is NOT a claim that any
OperationalSession runtime state machine, command execution, governance
enforcement, or provider behavior is implemented -- none is. No live
AI/agent provider call is made or required by any test in this module.
"""

import copy
import glob
import json
import os
import re
import unittest

import jsonschema
from referencing import Registry, Resource

CONTRACTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "contracts",
    "core",
)

EXPECTED_FILES = {
    "common-definitions.schema.json": "urn:cvf-operations-workspace:contracts:core:common-definitions:v1",
    "profile-manifest.schema.json": "urn:cvf-operations-workspace:contracts:core:profile-manifest:v1",
    "operational-session.schema.json": "urn:cvf-operations-workspace:contracts:core:operational-session:v1",
    "command-envelope.schema.json": "urn:cvf-operations-workspace:contracts:core:command-envelope:v1",
    "event-envelope.schema.json": "urn:cvf-operations-workspace:contracts:core:event-envelope:v1",
    "capability-manifest.schema.json": "urn:cvf-operations-workspace:contracts:core:capability-manifest:v1",
}

CONTRACT_OWNED = [
    "profile-manifest.schema.json",
    "operational-session.schema.json",
    "command-envelope.schema.json",
    "event-envelope.schema.json",
    "capability-manifest.schema.json",
]

PROVIDER_TOKENS = ["claude", "anthropic", "codex", "openai", "gpt", "alibaba", "qwen", "gemini"]


def _load_schemas():
    schemas = {}
    for name in EXPECTED_FILES:
        path = os.path.join(CONTRACTS_DIR, name)
        with open(path, encoding="utf-8") as fh:
            schemas[name] = json.load(fh)
    return schemas


def _load_raw_texts():
    raw = {}
    for name in EXPECTED_FILES:
        path = os.path.join(CONTRACTS_DIR, name)
        with open(path, encoding="utf-8") as fh:
            raw[name] = fh.read()
    return raw


def _build_registry(schemas):
    return Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values()
    )


def _validator_for(schemas, registry, name):
    return jsonschema.Draft202012Validator(
        schemas[name], registry=registry, format_checker=jsonschema.FormatChecker()
    )


def _is_valid(validator, instance):
    return len(list(validator.iter_errors(instance))) == 0


def _collect_refs(node, found):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                found.append(value)
            else:
                _collect_refs(value, found)
    elif isinstance(node, list):
        for item in node:
            _collect_refs(item, found)


PROFILE_MANIFEST_FIXTURE = {
    "profile_id": "shift-operations",
    "profile_version": "1.0.0",
    "display_name": "Shift Operations",
    "status": "contract-only",
    "owned_aggregates": ["shift", "task"],
    "supported_session_types": ["shift-session"],
    "commands": ["shift-close", "task-assign"],
    "events": ["shift-closed", "task-assigned"],
    "capability_dependencies": ["capability-notify"],
    "cvf_profile_extension": "cvf.profiles.shift_operations",
}

OPERATIONAL_SESSION_FIXTURE = {
    "session_id": "sess-0001",
    "workspace_id": "ws-shift-ops",
    "profile_id": "shift-operations",
    "profile_version": "1.0.0",
    "title": "Morning shift",
    "state": "ACTIVE",
    "participant_references": ["user-alice"],
    "ownership": {"owner_principal_id": "user-alice", "acquired_at": "2026-07-24T08:00:00Z"},
    "opened_at": "2026-07-24T08:00:00Z",
    "closed_at": None,
    "frozen_at": None,
    "policy_profile_id": "policy-default",
    "evidence_scope": ["evt-0001"],
    "metadata": {"note": "ok"},
    "version": 1,
}

COMMAND_ENVELOPE_FIXTURE = {
    "command_id": "cmd-0001",
    "workspace_id": "ws-shift-ops",
    "session_id": "sess-0001",
    "profile_id": "shift-operations",
    "profile_version": "1.0.0",
    "principal_id": "user-alice",
    "action": "shift-close",
    "risk_class": "R2",
    "evidence_references": ["evt-0001"],
    "idempotency_key": "idem-0001",
    "requested_at": "2026-07-24T08:05:00Z",
    "payload": {"reason": "end of shift"},
    "expected_version": 1,
}

EVENT_ENVELOPE_FIXTURE = {
    "event_id": "evt-0001",
    "event_type": "shift-closed",
    "profile_id": "shift-operations",
    "profile_version": "1.0.0",
    "session_id": "sess-0001",
    "source": "workspace-api",
    "data_state": "CONFIRMED",
    "evidence_references": ["evt-0001"],
    "created_by": "user-alice",
    "created_at": "2026-07-24T08:06:00Z",
    "payload": {"summary": "shift closed"},
    "correlation_id": "corr-0001",
    "causation_id": "cmd-0001",
    "sequence": 0,
}

CAPABILITY_MANIFEST_FIXTURE = {
    "capability_id": "capability-notify",
    "version": "1.0.0",
    "provider_id": "provider-generic",
    "status": "contract-only",
    "allowed_profiles": ["shift-operations"],
    "data_classification": ["operational"],
    "required_permissions": ["notify.send"],
    "risk_ceiling": "R1",
    "cost_policy": "flat-rate",
    "fallback": None,
    "termination_contract": "cancel-on-timeout",
    "input_schema": "urn:cvf-operations-workspace:contracts:core:notify-input:v1",
    "output_schema": "urn:cvf-operations-workspace:contracts:core:notify-output:v1",
}

FIXTURES = {
    "profile-manifest.schema.json": PROFILE_MANIFEST_FIXTURE,
    "operational-session.schema.json": OPERATIONAL_SESSION_FIXTURE,
    "command-envelope.schema.json": COMMAND_ENVELOPE_FIXTURE,
    "event-envelope.schema.json": EVENT_ENVELOPE_FIXTURE,
    "capability-manifest.schema.json": CAPABILITY_MANIFEST_FIXTURE,
}


class F1AContractsTestCase(unittest.TestCase):
    """Base class: loads schemas/registry once per test process."""

    @classmethod
    def setUpClass(cls):
        cls.schemas = _load_schemas()
        cls.raw_texts = _load_raw_texts()
        cls.registry = _build_registry(cls.schemas)

    def validator(self, name):
        return _validator_for(self.schemas, self.registry, name)

    def fixture(self, name):
        return copy.deepcopy(FIXTURES[name])


class TestF1AAC01FileAndIdentifierSet(F1AContractsTestCase):
    def test_exact_files_exist(self):
        on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(CONTRACTS_DIR, "*.schema.json"))}
        self.assertEqual(on_disk, set(EXPECTED_FILES.keys()))

    def test_exact_ids(self):
        for name, expected_id in EXPECTED_FILES.items():
            self.assertEqual(self.schemas[name]["$id"], expected_id)

    def test_no_other_schema_file_under_contracts(self):
        all_schema_files = glob.glob(
            os.path.join(os.path.dirname(CONTRACTS_DIR), "**", "*.schema.json"), recursive=True
        )
        self.assertEqual(len(all_schema_files), len(EXPECTED_FILES))


class TestF1AAC02Dialect(F1AContractsTestCase):
    def test_dialect_is_2020_12(self):
        for name, schema in self.schemas.items():
            self.assertEqual(
                schema["$schema"], "https://json-schema.org/draft/2020-12/schema", name
            )


class TestF1AAC03Parses(F1AContractsTestCase):
    def test_all_files_are_valid_json(self):
        for name in EXPECTED_FILES:
            path = os.path.join(CONTRACTS_DIR, name)
            with open(path, encoding="utf-8") as fh:
                json.load(fh)  # raises on failure

    def test_common_definitions_is_defs_only(self):
        cd = self.schemas["common-definitions.schema.json"]
        self.assertNotIn("type", cd)
        self.assertIn("$defs", cd)

    def test_contract_owned_schemas_are_type_object(self):
        for name in CONTRACT_OWNED:
            self.assertEqual(self.schemas[name]["type"], "object")


class TestF1AAC04MetaSchemaValidation(F1AContractsTestCase):
    def test_each_schema_validates_against_meta_schema(self):
        for name, schema in self.schemas.items():
            jsonschema.Draft202012Validator.check_schema(schema)


class TestF1AAC05OfflineRefResolution(F1AContractsTestCase):
    def test_no_http_ref_anywhere(self):
        for name, schema in self.schemas.items():
            refs = []
            _collect_refs(schema, refs)
            for ref in refs:
                self.assertFalse(
                    ref.startswith("http://") or ref.startswith("https://"),
                    f"{name} has network $ref: {ref}",
                )

    def test_no_http_substring_in_raw_text_ref_context(self):
        ref_pattern = re.compile(r'"\$ref"\s*:\s*"(https?://[^"]*)"')
        for name, text in self.raw_texts.items():
            match = ref_pattern.search(text)
            self.assertIsNone(match, f"{name} contains an http(s) $ref: {match}")

    def test_all_refs_resolve_in_offline_registry(self):
        for name in CONTRACT_OWNED:
            validator = self.validator(name)
            # Validating a real fixture forces every $ref along the way to resolve.
            errors = list(validator.iter_errors(self.fixture(name)))
            self.assertEqual(errors, [])


class TestF1AAC06PositiveInstances(F1AContractsTestCase):
    def test_positive_fixtures_validate(self):
        for name in CONTRACT_OWNED:
            validator = self.validator(name)
            self.assertTrue(_is_valid(validator, self.fixture(name)), name)


class TestF1AAC07MissingRequiredFields(F1AContractsTestCase):
    def test_missing_required_field_rejected(self):
        for name in CONTRACT_OWNED:
            validator = self.validator(name)
            fixture = self.fixture(name)
            required = self.schemas[name]["required"]
            field_to_drop = required[0]
            del fixture[field_to_drop]
            self.assertFalse(_is_valid(validator, fixture), f"{name} missing {field_to_drop}")


class TestF1AAC08UnknownContractOwnedProperties(F1AContractsTestCase):
    def test_unknown_top_level_property_rejected(self):
        for name in CONTRACT_OWNED:
            validator = self.validator(name)
            fixture = self.fixture(name)
            fixture["totally_unrecognized_field"] = "x"
            self.assertFalse(_is_valid(validator, fixture), name)

    def test_unknown_property_inside_ownership_rejected(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["ownership"]["unexpected_key"] = "x"
        self.assertFalse(_is_valid(validator, fixture))


class TestF1AAC09MalformedIdentifiers(F1AContractsTestCase):
    def test_session_id_with_space_rejected(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["session_id"] = "sess 0001"
        self.assertFalse(_is_valid(validator, fixture))

    def test_principal_id_too_long_rejected(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["principal_id"] = "a" * 200
        self.assertFalse(_is_valid(validator, fixture))


class TestF1AAC10SemVerGrammar(F1AContractsTestCase):
    REJECTED = ["01.0.0", "1.01.0", "1.0.01", "1.0.0-alpha", "1.0.0+build"]
    ACCEPTED = ["0.0.0", "1.0.0"]

    def test_profile_version_rejects_invalid_semver(self):
        validator = self.validator("profile-manifest.schema.json")
        for bad in self.REJECTED:
            fixture = self.fixture("profile-manifest.schema.json")
            fixture["profile_version"] = bad
            self.assertFalse(_is_valid(validator, fixture), bad)

    def test_profile_version_accepts_valid_semver(self):
        validator = self.validator("profile-manifest.schema.json")
        for good in self.ACCEPTED:
            fixture = self.fixture("profile-manifest.schema.json")
            fixture["profile_version"] = good
            self.assertTrue(_is_valid(validator, fixture), good)

    def test_capability_version_rejects_invalid_semver(self):
        validator = self.validator("capability-manifest.schema.json")
        for bad in self.REJECTED:
            fixture = self.fixture("capability-manifest.schema.json")
            fixture["version"] = bad
            self.assertFalse(_is_valid(validator, fixture), bad)

    def test_capability_version_accepts_valid_semver(self):
        validator = self.validator("capability-manifest.schema.json")
        for good in self.ACCEPTED:
            fixture = self.fixture("capability-manifest.schema.json")
            fixture["version"] = good
            self.assertTrue(_is_valid(validator, fixture), good)


class TestF1AAC11TimestampsFormatCheckerEnforced(F1AContractsTestCase):
    def test_structurally_malformed_timestamp_rejected(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["opened_at"] = "2026-07-24"  # bare date, no time
        self.assertFalse(_is_valid(validator, fixture))

        validator2 = self.validator("command-envelope.schema.json")
        fixture2 = self.fixture("command-envelope.schema.json")
        fixture2["requested_at"] = "not-a-date"
        self.assertFalse(_is_valid(validator2, fixture2))

    def test_calendrically_impossible_month_rejected(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["opened_at"] = "2026-13-01T00:00:00Z"
        self.assertFalse(_is_valid(validator, fixture))

        validator2 = self.validator("event-envelope.schema.json")
        fixture2 = self.fixture("event-envelope.schema.json")
        fixture2["created_at"] = "2026-13-01T00:00:00Z"
        self.assertFalse(_is_valid(validator2, fixture2))

    def test_calendrically_impossible_day_rejected(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["opened_at"] = "2026-02-30T00:00:00Z"
        self.assertFalse(_is_valid(validator, fixture))

        validator2 = self.validator("command-envelope.schema.json")
        fixture2 = self.fixture("command-envelope.schema.json")
        fixture2["requested_at"] = "2026-02-30T00:00:00Z"
        self.assertFalse(_is_valid(validator2, fixture2))

    def test_calendrically_impossible_hour_rejected(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["opened_at"] = "2026-07-24T25:00:00Z"
        self.assertFalse(_is_valid(validator, fixture))

        validator2 = self.validator("event-envelope.schema.json")
        fixture2 = self.fixture("event-envelope.schema.json")
        fixture2["created_at"] = "2026-07-24T25:00:00Z"
        self.assertFalse(_is_valid(validator2, fixture2))

    def test_valid_timestamps_still_accepted(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["opened_at"] = "2026-07-24T08:00:00.123+02:00"
        self.assertTrue(_is_valid(validator, fixture))


class TestF1AAC12InvalidOperationalSessionStates(F1AContractsTestCase):
    def test_invalid_state_rejected(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["state"] = "DELETED"
        self.assertFalse(_is_valid(validator, fixture))

    def test_all_six_valid_states_accepted(self):
        validator = self.validator("operational-session.schema.json")
        for state in ["DRAFT", "OPEN", "ACTIVE", "CLOSING", "CLOSED", "FROZEN"]:
            fixture = self.fixture("operational-session.schema.json")
            fixture["state"] = state
            self.assertTrue(_is_valid(validator, fixture), state)


class TestF1AAC13ExpectedVersion(F1AContractsTestCase):
    def test_zero_rejected(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["expected_version"] = 0
        self.assertFalse(_is_valid(validator, fixture))

    def test_negative_rejected(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["expected_version"] = -1
        self.assertFalse(_is_valid(validator, fixture))

    def test_non_integer_rejected(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["expected_version"] = "1"
        self.assertFalse(_is_valid(validator, fixture))

    def test_null_accepted(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["expected_version"] = None
        self.assertTrue(_is_valid(validator, fixture))


def _fixtures_have_consistent_identity(session, command):
    """Test-only helper. Never shipped outside the test suite (ADR-OW-005
    Decision 7 / F1A-AC-14): plain equality over two static fixtures, not a
    runtime enforcement mechanism."""
    return (
        session["profile_id"] == command["profile_id"]
        and session["profile_version"] == command["profile_version"]
    )


class TestF1AAC14CrossContractIdentityConsistency(F1AContractsTestCase):
    def test_matching_fixtures_are_consistent(self):
        session = self.fixture("operational-session.schema.json")
        command = self.fixture("command-envelope.schema.json")
        self.assertTrue(_fixtures_have_consistent_identity(session, command))

    def test_mismatched_profile_version_detected(self):
        session = self.fixture("operational-session.schema.json")
        command = self.fixture("command-envelope.schema.json")
        command["profile_version"] = "2.0.0"
        self.assertFalse(_fixtures_have_consistent_identity(session, command))


class TestF1AAC15InvalidCapabilityDeclarations(F1AContractsTestCase):
    def test_invalid_status_rejected(self):
        validator = self.validator("capability-manifest.schema.json")
        fixture = self.fixture("capability-manifest.schema.json")
        fixture["status"] = "beta"
        self.assertFalse(_is_valid(validator, fixture))

    def test_non_string_in_allowed_profiles_rejected(self):
        validator = self.validator("capability-manifest.schema.json")
        fixture = self.fixture("capability-manifest.schema.json")
        fixture["allowed_profiles"] = [123]
        self.assertFalse(_is_valid(validator, fixture))


class TestF1AAC16ProfileManifestContract(F1AContractsTestCase):
    def test_required_fields(self):
        schema = self.schemas["profile-manifest.schema.json"]
        self.assertEqual(
            set(schema["required"]),
            {
                "profile_id",
                "profile_version",
                "display_name",
                "status",
                "owned_aggregates",
                "supported_session_types",
                "commands",
                "events",
                "capability_dependencies",
                "cvf_profile_extension",
            },
        )

    def test_status_enum_closed(self):
        schema = self.schemas["profile-manifest.schema.json"]
        self.assertEqual(
            set(schema["properties"]["status"]["enum"]),
            {"planned", "contract-only", "partial", "pilot", "frozen"},
        )


class TestF1AAC17OperationalSessionContract(F1AContractsTestCase):
    def test_required_fields(self):
        schema = self.schemas["operational-session.schema.json"]
        self.assertEqual(
            set(schema["required"]),
            {
                "session_id",
                "workspace_id",
                "profile_id",
                "profile_version",
                "title",
                "state",
                "participant_references",
                "opened_at",
                "policy_profile_id",
                "evidence_scope",
                "metadata",
                "version",
            },
        )

    def test_version_is_optimistic_concurrency_integer(self):
        schema = self.schemas["operational-session.schema.json"]
        self.assertEqual(schema["properties"]["version"]["type"], "integer")
        self.assertEqual(schema["properties"]["version"]["minimum"], 1)

    def test_ownership_closed_when_present(self):
        schema = self.schemas["operational-session.schema.json"]
        ownership = schema["properties"]["ownership"]
        self.assertFalse(ownership["additionalProperties"])
        self.assertEqual(set(ownership["required"]), {"owner_principal_id", "acquired_at"})


class TestF1AAC18CommandEnvelopeContract(F1AContractsTestCase):
    def test_required_fields(self):
        schema = self.schemas["command-envelope.schema.json"]
        self.assertEqual(
            set(schema["required"]),
            {
                "command_id",
                "workspace_id",
                "session_id",
                "profile_id",
                "profile_version",
                "principal_id",
                "action",
                "risk_class",
                "evidence_references",
                "idempotency_key",
                "requested_at",
                "payload",
                "expected_version",
            },
        )

    def test_risk_class_enum_closed(self):
        schema = self.schemas["command-envelope.schema.json"]
        risk_ref = schema["properties"]["risk_class"]["$ref"]
        risk_class_def = self.schemas["common-definitions.schema.json"]["$defs"]["riskClass"]
        self.assertTrue(risk_ref.endswith("#/$defs/riskClass"))
        self.assertEqual(set(risk_class_def["enum"]), {"R0", "R1", "R2", "R3"})


class TestF1AAC19EventEnvelopeContract(F1AContractsTestCase):
    def test_required_fields(self):
        schema = self.schemas["event-envelope.schema.json"]
        self.assertEqual(
            set(schema["required"]),
            {
                "event_id",
                "event_type",
                "profile_id",
                "profile_version",
                "session_id",
                "source",
                "data_state",
                "evidence_references",
                "created_by",
                "created_at",
                "payload",
                "correlation_id",
                "causation_id",
                "sequence",
            },
        )

    def test_data_state_enum_closed(self):
        schema = self.schemas["event-envelope.schema.json"]
        self.assertEqual(
            set(schema["properties"]["data_state"]["enum"]),
            {"RAW", "NORMALIZED", "PROPOSED", "CONFIRMED", "REJECTED", "CORRECTED", "FROZEN"},
        )

    def test_sequence_is_non_negative_integer(self):
        schema = self.schemas["event-envelope.schema.json"]
        self.assertEqual(schema["properties"]["sequence"]["type"], "integer")
        self.assertEqual(schema["properties"]["sequence"]["minimum"], 0)

    def test_causation_id_nullable(self):
        validator = self.validator("event-envelope.schema.json")
        fixture = self.fixture("event-envelope.schema.json")
        fixture["causation_id"] = None
        self.assertTrue(_is_valid(validator, fixture))


class TestF1AAC20CapabilityManifestContract(F1AContractsTestCase):
    def test_required_fields(self):
        schema = self.schemas["capability-manifest.schema.json"]
        self.assertEqual(
            set(schema["required"]),
            {
                "capability_id",
                "version",
                "provider_id",
                "status",
                "allowed_profiles",
                "data_classification",
                "required_permissions",
                "risk_ceiling",
                "cost_policy",
                "termination_contract",
                "input_schema",
                "output_schema",
            },
        )

    def test_status_enum_closed(self):
        schema = self.schemas["capability-manifest.schema.json"]
        self.assertEqual(
            set(schema["properties"]["status"]["enum"]),
            {"stub", "contract-only", "partial", "pilot", "production"},
        )


class TestF1AAC21OpaqueBoundariesCannotBypassTopLevelClosure(F1AContractsTestCase):
    def test_command_envelope_top_level_unknown_rejected_payload_open(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["payload"] = {"anything": "goes", "nested": {"more": 1}}
        self.assertTrue(_is_valid(validator, fixture))
        fixture["not_a_real_field"] = "x"
        self.assertFalse(_is_valid(validator, fixture))

    def test_event_envelope_top_level_unknown_rejected_payload_open(self):
        validator = self.validator("event-envelope.schema.json")
        fixture = self.fixture("event-envelope.schema.json")
        fixture["payload"] = {"anything": "goes"}
        self.assertTrue(_is_valid(validator, fixture))
        fixture["not_a_real_field"] = "x"
        self.assertFalse(_is_valid(validator, fixture))


class TestF1AAC22NoProviderSpecificFields(F1AContractsTestCase):
    def test_no_provider_tokens_in_any_schema_text(self):
        for name, text in self.raw_texts.items():
            lowered = text.lower()
            for token in PROVIDER_TOKENS:
                self.assertNotIn(token, lowered, f"{name} contains provider token '{token}'")


class TestF1AAC23ClaimBoundaryStatementPresent(F1AContractsTestCase):
    def test_module_docstring_states_claim_boundary(self):
        doc = (__doc__ or "").lower()
        self.assertIn("contract", doc)
        self.assertIn("no", doc)
        self.assertIn("runtime", doc)
        self.assertIn("provider", doc)

    def test_schema_descriptions_state_contract_only(self):
        for name in CONTRACT_OWNED:
            description = self.schemas[name].get("description", "")
            self.assertIn("Contract-only", description, name)
            self.assertIn("no runtime state machine", description, name)


class TestF1AAC30FormatCheckerLoadBearing(F1AContractsTestCase):
    def test_date_time_checker_is_registered(self):
        checker = jsonschema.FormatChecker()
        self.assertIn("date-time", checker.checkers)

    def test_every_validator_in_suite_has_format_checker(self):
        for name in CONTRACT_OWNED:
            validator = self.validator(name)
            self.assertIsNotNone(validator.format_checker)


class TestF1AAC31OpaqueNestedKeysNeverBypassClosedEnvelope(F1AContractsTestCase):
    def test_arbitrary_nested_metadata_keys_accepted(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        fixture["metadata"] = {"anything": "goes", "another": {"nested": True}}
        self.assertTrue(_is_valid(validator, fixture))

    def test_arbitrary_nested_payload_keys_accepted(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["payload"] = {"anything": "goes"}
        self.assertTrue(_is_valid(validator, fixture))

    def test_same_unknown_key_at_top_level_rejected(self):
        validator = self.validator("command-envelope.schema.json")
        fixture = self.fixture("command-envelope.schema.json")
        fixture["some_extension_key"] = "x"
        self.assertFalse(_is_valid(validator, fixture))

    def test_nested_state_key_does_not_satisfy_required_top_level_state(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        del fixture["state"]
        fixture["metadata"] = {"state": "FROZEN"}
        self.assertFalse(_is_valid(validator, fixture))

    def test_nested_version_key_does_not_satisfy_required_top_level_version(self):
        validator = self.validator("operational-session.schema.json")
        fixture = self.fixture("operational-session.schema.json")
        del fixture["version"]
        fixture["metadata"] = {"version": 999}
        self.assertFalse(_is_valid(validator, fixture))


if __name__ == "__main__":
    unittest.main()

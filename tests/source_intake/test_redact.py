from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "source_intake" / "redact.py"
SPEC = importlib.util.spec_from_file_location("si_redact", MODULE_PATH)
assert SPEC and SPEC.loader
redact = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(redact)


class RedactCredentialUrlTests(unittest.TestCase):
    def test_simple_username_password_is_redacted(self) -> None:
        result = redact.redact_credential_urls("https://user:hunter2@github.com/org/repo.git")
        self.assertEqual(result, "https://<redacted>@github.com/org/repo.git")
        self.assertNotIn("hunter2", result)

    def test_username_only_is_redacted(self) -> None:
        result = redact.redact_credential_urls("https://token@github.com/org/repo.git")
        self.assertEqual(result, "https://<redacted>@github.com/org/repo.git")
        self.assertNotIn("token", result)

    def test_password_containing_multiple_at_signs_leaks_no_fragment(self) -> None:
        # This is the case the old verifier's '[^/@\\s]+@' pattern got wrong:
        # it matched only up to the FIRST '@', leaving 'ss@host' visible and
        # exposing 'ss' (part of the actual password) as if it were a host
        # fragment. The fix must redact through the LAST '@' before '/'.
        url = "https://user:pa@ss@w0rd@github.com/org/repo.git"
        result = redact.redact_credential_urls(url)
        self.assertEqual(result, "https://<redacted>@github.com/org/repo.git")
        self.assertNotIn("pa@ss@w0rd", result)
        self.assertNotIn("ss@w0rd", result)
        self.assertNotIn("w0rd", result)

    def test_plain_url_without_credentials_is_unchanged(self) -> None:
        url = "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"
        self.assertEqual(redact.redact_credential_urls(url), url)

    def test_at_sign_in_path_is_left_alone(self) -> None:
        url = "https://api.example.com/@handle/profile"
        self.assertEqual(redact.redact_credential_urls(url), url)

    def test_non_url_text_is_unaffected(self) -> None:
        text = "ordinary git status output with no urls at all"
        self.assertEqual(redact.redact_credential_urls(text), text)

    def test_redact_lines_applies_to_every_line(self) -> None:
        lines = [
            "clean line",
            "https://user:secret@example.com/path",
        ]
        result = redact.redact_lines(lines)
        self.assertEqual(result[0], "clean line")
        self.assertNotIn("secret", result[1])


if __name__ == "__main__":
    unittest.main()

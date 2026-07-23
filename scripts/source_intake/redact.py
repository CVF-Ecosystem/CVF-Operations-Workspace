"""Credential-safe redaction for URLs that may appear in captured evidence.

Git remote output, provider error text, and other captured strings can
contain ``https://user:password@host/...`` URLs. Every string F0 writes to
disk must pass through this module first.
"""

from __future__ import annotations

import re

# Greedy: '[^/\s]*' consumes as much of the userinfo+host run as possible,
# then backtracks only as far as needed to find a trailing literal '@'.
# That means it anchors on the LAST '@' before the next '/' or whitespace,
# not the first. A naive '[^/@\s]+@' (first '@' only) leaks a fragment of
# the password when the password itself contains '@', e.g.
# 'https://user:pa@ss@host/path' would redact to
# 'https://<redacted>@ss@host/path' with the old pattern, exposing 'ss'.
# The greedy pattern below redacts the whole userinfo run and correctly
# leaves 'host' untouched: 'https://<redacted>@host/path'.
_CREDENTIAL_URL = re.compile(r"(https?://)[^/\s]*@")


def redact_credential_urls(text: str) -> str:
    """Replace URL userinfo (user[:password]) with '<redacted>@'.

    Safe against multiple '@' characters inside the userinfo segment and
    against '@' characters that legitimately appear later in the path
    (those are never touched, because matching stops at the first '/').
    """
    return _CREDENTIAL_URL.sub(r"\1<redacted>@", text)


def redact_lines(lines: list[str]) -> list[str]:
    return [redact_credential_urls(line) for line in lines]

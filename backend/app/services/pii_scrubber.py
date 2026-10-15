"""Redact common credentials and personal identifiers from captured state."""

import re
from typing import Any, Dict, Tuple

REDACTED = "[REDACTED]"

_EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)
_JWT_PATTERN = re.compile(
    r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\b"
)
_BEARER_PATTERN = re.compile(
    r"\bBearer\s+[A-Za-z0-9._~+/-]+=*",
    re.IGNORECASE,
)
_API_TOKEN_PATTERN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})\b"
)
_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"""(?i)(?P<prefix>\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|"""
    r"""passwd|secret|authorization)\b["']?\s*[:=]\s*)"""
    r"""(?P<secret>"[^"]*"|'[^']*'|[^\s,;}]+)"""
)
_SENSITIVE_KEY_PARTS = (
    "apikey",
    "accesstoken",
    "refreshtoken",
    "token",
    "authorization",
    "password",
    "passwd",
    "secret",
    "privatekey",
    "cookie",
    "email",
    "phone",
    "mobile",
    "ssn",
    "fullname",
    "firstname",
    "lastname",
    "displayname",
    "username",
    "userid",
    "address",
    "dateofbirth",
    "dob",
)


def scrub_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a recursively scrubbed JSON-compatible state mapping."""
    return {
        scrub_text(key): REDACTED if _is_sensitive_key(key) else _scrub_value(value)
        for key, value in state.items()
    }


def scrub_text(value: str) -> str:
    """Redact common sensitive values embedded in free text."""
    scrubbed = _BEARER_PATTERN.sub(f"Bearer {REDACTED}", value)
    scrubbed = _JWT_PATTERN.sub(REDACTED, scrubbed)
    scrubbed = _API_TOKEN_PATTERN.sub(REDACTED, scrubbed)
    scrubbed = _EMAIL_PATTERN.sub(REDACTED, scrubbed)
    return _SECRET_ASSIGNMENT_PATTERN.sub(_redact_secret_assignment, scrubbed)


def scrub_diff_values(path: str, before: Any, after: Any) -> Tuple[Any, Any]:
    """Redact diff values without hiding whether protected values changed."""
    path_parts = (
        part.replace("~1", "/").replace("~0", "~")
        for part in path.split("/")
        if part
    )
    if any(_is_sensitive_key(part) for part in path_parts):
        return (
            REDACTED if before is not None else None,
            REDACTED if after is not None else None,
        )
    return _scrub_value(before), _scrub_value(after)


def _is_sensitive_key(key: str) -> bool:
    normalized_key = re.sub(r"[^a-z0-9]", "", key.lower())
    return normalized_key == "name" or any(
        part in normalized_key for part in _SENSITIVE_KEY_PARTS
    )


def _redact_secret_assignment(match: re.Match) -> str:
    secret = match.group("secret")
    if secret.startswith(("'", '"')):
        return f"{match.group('prefix')}{secret[0]}{REDACTED}{secret[0]}"
    return f"{match.group('prefix')}{REDACTED}"


def _scrub_value(value: Any) -> Any:
    if isinstance(value, dict):
        return scrub_state(value)
    if isinstance(value, list):
        return [_scrub_value(item) for item in value]
    if isinstance(value, str):
        return scrub_text(value)
    return value

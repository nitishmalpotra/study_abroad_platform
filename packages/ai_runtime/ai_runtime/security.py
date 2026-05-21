import re


_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{12,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{16,}"),
    re.compile(r"(?i)(authorization\s*:\s*)(?:bearer\s+)?([^\s,;]+)"),
    re.compile(
        r"(?i)(api[_-]?key|token|secret)(\s*[=:]\s*)([^\s,;]+)"
    ),
    re.compile(r"(?i)(bearer)(\s+)([^\s,;]+)"),
)


def redact_secrets(value: object) -> str:
    redacted = str(value)
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(_redacted_match, redacted)
    return redacted


def _redacted_match(match: re.Match[str]) -> str:
    if match.lastindex == 2:
        return f"{match.group(1)}[REDACTED_API_KEY]"
    if match.lastindex == 3:
        return f"{match.group(1)}{match.group(2)}[REDACTED_API_KEY]"
    return "[REDACTED_API_KEY]"

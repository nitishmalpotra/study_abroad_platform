import re


def sanitize_text(value: str, *, max_length: int | None = None) -> str:
    cleaned = re.sub(r"[\x00-\x1F\x7F]+", " ", str(value or ""))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if max_length is not None:
        cleaned = cleaned[:max_length]
    return cleaned

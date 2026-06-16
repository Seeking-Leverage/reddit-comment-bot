import re
from typing import List, Optional, Tuple

from bot.models import CommentContext

BLOCKED_PATTERNS = [
    r"https?://",
    r"\bwww\.",
    r"\bcheck out\b",
    r"\bDM me\b",
    r"\b(sign up|free trial|buy now)\b",
    r"^great question\b",
    r"\bhope this helps\b",
    r"^as someone who\b",
]


def validate_comment(text: str, ctx: CommentContext) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    cleaned = text.strip()

    if len(cleaned) < ctx.min_chars:
        reasons.append("too_short")
    if len(cleaned) > ctx.max_chars:
        reasons.append("too_long")

    lowered = cleaned.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            reasons.append(f"blocked:{pattern}")
            break

    if ctx.client_name and ctx.client_name.lower() in lowered:
        reasons.append("mentions_client")

    return len(reasons) == 0, reasons
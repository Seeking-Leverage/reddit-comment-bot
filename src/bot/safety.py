import re
from typing import List, Tuple

from bot.models import CommentContext, PromoLevel

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


def _mentions_term(text: str, term: str) -> bool:
    term = term.strip()
    if not term or len(term) < 3:
        return False
    return re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE) is not None


def _mentions_any_phrase(text: str, blob: str, *, min_word_len: int = 4) -> bool:
    """Check if any significant word from blob appears in text."""
    if not blob.strip():
        return False
    words = [w for w in re.findall(r"[a-zA-Z0-9]+", blob) if len(w) >= min_word_len]
    lowered = text.lower()
    return any(word.lower() in lowered for word in words[:8])


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

    company = ctx.company or ctx.client_name
    product = ctx.product
    competitors = ctx.competitors

    if ctx.promo_level == "none":
        if company and _mentions_term(cleaned, company):
            reasons.append("mentions_company_at_none")
        if product and _mentions_any_phrase(cleaned, product):
            reasons.append("mentions_product_at_none")
        if competitors and _mentions_any_phrase(cleaned, competitors):
            reasons.append("mentions_competitors_at_none")

    elif ctx.promo_level == "low":
        if competitors and _mentions_any_phrase(cleaned, competitors):
            reasons.append("mentions_competitors_at_low")

    return len(reasons) == 0, reasons
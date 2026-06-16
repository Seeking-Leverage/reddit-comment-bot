from dataclasses import dataclass, field
from typing import List, Literal, Optional

Tone = Literal["funny", "data-driven", "direct"]
PromoLevel = Literal["none", "low", "moderate"]


@dataclass(frozen=True)
class CommentContext:
    """Everything needed to generate one comment."""

    title: str
    subreddit: str
    body: str
    parent_comment: Optional[str] = None
    industry: str = ""
    expertise: str = ""
    subreddit_note: str = ""
    tone: Tone = "data-driven"
    promo_level: PromoLevel = "none"
    product: str = ""
    company: str = ""
    competitors: str = ""
    client_name: str = ""
    max_chars: int = 400
    min_chars: int = 40
    max_retries: int = 1


@dataclass
class CommentResult:
    text: str
    ok: bool
    attempts: int = 0
    model: str = ""
    reject_reasons: List[str] = field(default_factory=list)
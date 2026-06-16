from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Tone = Literal["funny", "data-driven", "direct"]
PromoLevel = Literal["none", "low", "moderate"]
CommentStatus = Literal["draft", "posted", "skipped"]


class BrandProfile(BaseModel):
    product: str = ""
    company: str = ""
    competitors: str = ""
    expertise_summary: str = ""
    industry: str = ""
    goals: str = ""


class PlaybookEntry(BaseModel):
    subreddit: str = Field(..., min_length=1, max_length=100)
    summary: str = ""
    tone: Tone = "data-driven"
    promo_level: PromoLevel = "none"
    angles: List[str] = Field(default_factory=list)
    dos_donts: str = ""


class GenerateCommentRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subreddit: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=8000)
    parent_comment: Optional[str] = Field(default=None, max_length=2000)


class GenerateCommentResponse(BaseModel):
    comment: str
    ok: bool
    attempts: int = 0
    model: str = ""
    reject_reasons: List[str] = Field(default_factory=list)


class HistoryEntry(BaseModel):
    id: str
    created_at: str
    subreddit: str
    title: str
    description: str = ""
    parent_comment: str = ""
    generated_comment: str
    final_comment: str = ""
    status: CommentStatus = "draft"
    post_url: str = ""


class HistoryCreate(BaseModel):
    subreddit: str
    title: str
    description: str = ""
    parent_comment: str = ""
    generated_comment: str
    final_comment: str = ""
    status: CommentStatus = "draft"
    post_url: str = ""


class TrackerGoals(BaseModel):
    goal_upvotes: int = 100
    goal_impressions: int = 2000


class TrackerEntry(BaseModel):
    id: str
    created_at: str
    history_id: Optional[str] = None
    post_url: str = ""
    subreddit: str = ""
    upvotes: int = 0
    impressions: int = 0
    notes: str = ""


class TrackerEntryCreate(BaseModel):
    history_id: Optional[str] = None
    post_url: str = ""
    subreddit: str = ""
    upvotes: int = 0
    impressions: int = 0
    notes: str = ""


class TrackerTotals(BaseModel):
    upvotes: int = 0
    impressions: int = 0


class TrackerSummary(BaseModel):
    goals: TrackerGoals
    totals: TrackerTotals
    entries: List[TrackerEntry]
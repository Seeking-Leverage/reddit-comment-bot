from pathlib import Path
from typing import Dict, Literal, Optional

import yaml
from pydantic import BaseModel, Field

Tone = Literal["funny", "data-driven", "direct"]


class RedditAccountConfig(BaseModel):
    username: str
    client_id: str
    client_secret: str
    password: str
    user_agent: str = "reddit-comment-bot/0.2 (agency engagement tool)"


class FocusArea(BaseModel):
    name: str
    description: str
    subreddits: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class EngagementRules(BaseModel):
    max_comments_per_run: int = 2
    max_comments_per_day: int = 10
    min_post_score: int = 1
    max_post_age_hours: int = 4
    post_sort: Literal["new", "rising", "hot"] = "rising"
    min_seconds_between_comments: int = 600
    reply_to_top_comments: bool = True
    max_top_comments_to_consider: int = 3


class VoiceConfig(BaseModel):
    tone: Tone = "data-driven"
    max_chars: int = 400
    min_chars: int = 40
    max_retries: int = 1


class ClientConfig(BaseModel):
    client_id: str
    client_name: str
    industry: str
    expertise_summary: str
    reddit_account: RedditAccountConfig
    focus_areas: list[FocusArea]
    subreddit_notes: Dict[str, str] = Field(default_factory=dict)
    engagement: EngagementRules = Field(default_factory=EngagementRules)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    dry_run: bool = True

    def note_for(self, subreddit: str) -> str:
        key = subreddit.lower().removeprefix("r/").removeprefix("/")
        return self.subreddit_notes.get(key, "")


def load_client_config(path: Path) -> ClientConfig:
    with path.open() as f:
        raw = yaml.safe_load(f)
    return ClientConfig.model_validate(raw)


def list_client_configs(config_dir: Path) -> list[Path]:
    if not config_dir.exists():
        return []
    return sorted(config_dir.glob("*.yaml"))
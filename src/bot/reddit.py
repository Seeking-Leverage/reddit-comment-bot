from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import praw
from praw.models import Comment, Submission

from bot.config import ClientConfig, RedditAccountConfig


@dataclass
class PostCandidate:
    submission: Submission
    subreddit: str
    focus_area: str


@dataclass
class CommentCandidate:
    comment: Comment
    submission: Submission
    subreddit: str
    focus_area: str


class RedditClient:
    def __init__(self, account: RedditAccountConfig):
        self.account = account
        self._reddit = praw.Reddit(
            client_id=account.client_id,
            client_secret=account.client_secret,
            username=account.username,
            password=account.password,
            user_agent=account.user_agent,
        )

    @property
    def username(self) -> str:
        return self.account.username

    def fetch_posts(
        self,
        config: ClientConfig,
        *,
        limit_per_subreddit: int = 25,
    ) -> list[PostCandidate]:
        candidates: list[PostCandidate] = []
        seen_ids: set[str] = set()

        for area in config.focus_areas:
            for sub_name in area.subreddits:
                subreddit = self._reddit.subreddit(sub_name)
                sort = config.engagement.post_sort
                submissions = getattr(subreddit, sort)(limit=limit_per_subreddit)

                for submission in submissions:
                    if submission.id in seen_ids:
                        continue
                    if not self._post_matches(submission, config, area.keywords):
                        continue
                    seen_ids.add(submission.id)
                    candidates.append(
                        PostCandidate(
                            submission=submission,
                            subreddit=sub_name,
                            focus_area=area.name,
                        )
                    )

        return candidates

    def top_comments(self, submission: Submission, limit: int) -> list[Comment]:
        submission.comments.replace_more(limit=0)
        comments = [
            c
            for c in submission.comments
            if isinstance(c, Comment) and c.body not in ("[deleted]", "[removed]")
        ]
        comments.sort(key=lambda c: c.score, reverse=True)
        return comments[:limit]

    def post_comment(
        self,
        submission: Submission,
        text: str,
        *,
        parent_comment: Optional[Comment] = None,
    ) -> Comment:
        if parent_comment:
            return parent_comment.reply(text)
        return submission.reply(text)

    def _post_matches(
        self,
        submission: Submission,
        config: ClientConfig,
        keywords: list[str],
    ) -> bool:
        rules = config.engagement

        if submission.stickied:
            return False
        if submission.score < rules.min_post_score:
            return False

        age_hours = (
            datetime.now(timezone.utc).timestamp() - submission.created_utc
        ) / 3600
        if age_hours > rules.max_post_age_hours:
            return False

        if keywords:
            haystack = f"{submission.title} {submission.selftext}".lower()
            if not any(kw.lower() in haystack for kw in keywords):
                return False

        return True
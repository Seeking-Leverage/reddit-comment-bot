import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Union

from rich.console import Console

from bot.config import ClientConfig, FocusArea
from bot.db import Database
from bot.generation import CommentGenerator
from bot.reddit import CommentCandidate, PostCandidate, RedditClient

console = Console()
logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    client_id: str
    posts_scanned: int
    comments_attempted: int
    comments_posted: int
    comments_skipped: int
    dry_run: bool


class BotOrchestrator:
    def __init__(
        self,
        config: ClientConfig,
        *,
        db: Optional[Database] = None,
        generator: Optional[CommentGenerator] = None,
    ):
        self.config = config
        self.db = db or Database()
        self.reddit = RedditClient(config.reddit_account)
        self.generator = generator or CommentGenerator()

    def run(self) -> RunResult:
        cfg = self.config
        rules = cfg.engagement
        focus_by_name = {a.name: a for a in cfg.focus_areas}

        posts = self.reddit.fetch_posts(cfg)
        posts_scanned = len(posts)

        daily_count = self.db.count_comments_today(cfg.client_id)
        if daily_count >= rules.max_comments_per_day:
            console.print(
                f"[yellow]Daily limit reached ({daily_count}/{rules.max_comments_per_day})[/]"
            )
            return RunResult(cfg.client_id, posts_scanned, 0, 0, 0, cfg.dry_run)

        last_at = self.db.last_comment_at(cfg.client_id)
        if last_at:
            elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
            if elapsed < rules.min_seconds_between_comments:
                console.print("[yellow]Cooldown active — skipping run[/]")
                return RunResult(cfg.client_id, posts_scanned, 0, 0, 0, cfg.dry_run)

        attempted = 0
        posted = 0
        skipped = 0
        remaining_daily = rules.max_comments_per_day - daily_count
        max_this_run = min(rules.max_comments_per_run, remaining_daily)

        for post_candidate in posts:
            if posted >= max_this_run:
                break

            submission = post_candidate.submission
            if self.db.has_engaged_post(cfg.client_id, submission.id):
                skipped += 1
                continue

            focus_area = focus_by_name.get(post_candidate.focus_area)
            if not focus_area:
                skipped += 1
                continue

            targets = self._build_targets(post_candidate)
            if not targets:
                skipped += 1
                continue

            for target in targets:
                if posted >= max_this_run:
                    break
                attempted += 1

                result = self._generate(target, focus_area)
                if not result.ok:
                    skipped += 1
                    reasons = ", ".join(result.reject_reasons[-3:]) or "validation_failed"
                    console.print(
                        f"[red]Skipped[/] post={submission.id} ({reasons})"
                    )
                    self.db.record_comment(
                        client_id=cfg.client_id,
                        reddit_username=self.reddit.username,
                        post_id=submission.id,
                        subreddit=post_candidate.subreddit,
                        generated_text=result.text,
                        status="rejected",
                        parent_id=self._parent_id(target),
                    )
                    continue

                text = result.text
                if cfg.dry_run:
                    self._log_dry_run(target, text, result.attempts)
                    self.db.record_comment(
                        client_id=cfg.client_id,
                        reddit_username=self.reddit.username,
                        post_id=submission.id,
                        subreddit=post_candidate.subreddit,
                        generated_text=text,
                        status="dry_run",
                        parent_id=self._parent_id(target),
                    )
                    posted += 1
                    continue

                comment = self.reddit.post_comment(
                    submission,
                    text,
                    parent_comment=self._parent_comment(target),
                )
                self.db.record_comment(
                    client_id=cfg.client_id,
                    reddit_username=self.reddit.username,
                    post_id=submission.id,
                    subreddit=post_candidate.subreddit,
                    generated_text=text,
                    status="posted",
                    comment_id=comment.id,
                    parent_id=comment.parent_id,
                )
                posted += 1
                console.print(
                    f"[green]Posted[/] r/{post_candidate.subreddit} — {comment.permalink}"
                )

        return RunResult(
            client_id=cfg.client_id,
            posts_scanned=posts_scanned,
            comments_attempted=attempted,
            comments_posted=posted,
            comments_skipped=skipped,
            dry_run=cfg.dry_run,
        )

    def _build_targets(
        self,
        post_candidate: PostCandidate,
    ) -> List[Union[PostCandidate, CommentCandidate]]:
        submission = post_candidate.submission
        rules = self.config.engagement

        if rules.reply_to_top_comments:
            top = self.reddit.top_comments(
                submission,
                rules.max_top_comments_to_consider,
            )
            if top:
                return [
                    CommentCandidate(
                        comment=c,
                        submission=submission,
                        subreddit=post_candidate.subreddit,
                        focus_area=post_candidate.focus_area,
                    )
                    for c in top
                ]

        return [post_candidate]

    def _generate(
        self,
        target: Union[PostCandidate, CommentCandidate],
        focus_area: FocusArea,
    ):
        if isinstance(target, CommentCandidate):
            return self.generator.for_reply(self.config, target, focus_area)
        return self.generator.for_post(self.config, target, focus_area)

    @staticmethod
    def _parent_comment(target: Union[PostCandidate, CommentCandidate]):
        if isinstance(target, CommentCandidate):
            return target.comment
        return None

    @staticmethod
    def _parent_id(target: Union[PostCandidate, CommentCandidate]) -> Optional[str]:
        if isinstance(target, CommentCandidate):
            return target.comment.id
        return None

    def _log_dry_run(
        self,
        target: Union[PostCandidate, CommentCandidate],
        text: str,
        attempts: int,
    ) -> None:
        sub = target.subreddit
        post_id = target.submission.id
        kind = "reply" if isinstance(target, CommentCandidate) else "top-level"
        console.print(
            f"[cyan]DRY RUN[/] r/{sub} post={post_id} ({kind}, {attempts} attempt(s))"
        )
        console.print(f"  {text[:200]}{'...' if len(text) > 200 else ''}")
import logging
from typing import Optional, Union

from bot.config import ClientConfig, FocusArea
from bot.llm import LLMClient
from bot.models import CommentContext, CommentResult
from bot.prompts import build_system_prompt, build_user_prompt
from bot.reddit import CommentCandidate, PostCandidate
from bot.safety import validate_comment
from bot.settings import settings

logger = logging.getLogger(__name__)


class CommentGenerator:
    def __init__(self, llm: Optional[LLMClient] = None) -> None:
        self._llm = llm

    def from_context(self, ctx: CommentContext) -> CommentResult:
        """Generate a comment from a pre-built context (API / manual capture)."""
        return self._generate(ctx)

    def for_post(
        self,
        config: ClientConfig,
        candidate: PostCandidate,
        focus_area: FocusArea,
    ) -> CommentResult:
        return self._generate(self._context(config, candidate, focus_area))

    def for_reply(
        self,
        config: ClientConfig,
        candidate: CommentCandidate,
        focus_area: FocusArea,
    ) -> CommentResult:
        return self._generate(
            self._context(
                config,
                candidate,
                focus_area,
                parent_comment=candidate.comment.body,
            )
        )

    def _context(
        self,
        config: ClientConfig,
        candidate: Union[PostCandidate, CommentCandidate],
        focus_area: FocusArea,
        *,
        parent_comment: Optional[str] = None,
    ) -> CommentContext:
        submission = candidate.submission
        body = (submission.selftext or "")[: settings.max_post_chars]
        parent = (parent_comment or "")[: settings.max_parent_comment_chars] or None

        return CommentContext(
            title=submission.title[:500],
            subreddit=candidate.subreddit,
            body=body,
            parent_comment=parent,
            industry=config.industry,
            expertise=config.expertise_summary,
            subreddit_note=config.note_for(candidate.subreddit),
            tone=config.voice.tone,
            client_name=config.client_name,
            max_chars=config.voice.max_chars,
            min_chars=config.voice.min_chars,
            max_retries=config.voice.max_retries,
        )

    def _generate(self, ctx: CommentContext) -> CommentResult:
        llm = self._llm or LLMClient()
        system = build_system_prompt(ctx)
        user = build_user_prompt(ctx)
        max_attempts = ctx.max_retries + 1

        rejected: list[str] = []
        text = ""
        attempts = 0
        model = settings.llm_model

        for _ in range(max_attempts):
            attempts += 1
            try:
                response = llm.complete(system=system, user=user)
                text = response.text[: ctx.max_chars]
                model = response.model
            except Exception as exc:
                logger.error("LLM call failed attempt=%s error=%s", attempts, exc)
                rejected.append(f"api_error:{type(exc).__name__}")
                continue

            ok, reasons = validate_comment(text, ctx)
            if ok:
                return CommentResult(
                    text=text,
                    ok=True,
                    attempts=attempts,
                    model=model,
                )
            rejected.extend(reasons)
            logger.info("Comment rejected attempt=%s reasons=%s", attempts, reasons)

        return CommentResult(
            text=text,
            ok=False,
            attempts=attempts,
            model=model,
            reject_reasons=rejected,
        )
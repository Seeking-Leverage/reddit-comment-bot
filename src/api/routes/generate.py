from fastapi import APIRouter, HTTPException

from api.schemas import GenerateCommentRequest, GenerateCommentResponse
from api.storage import DataStore, playbook_note
from bot.generation import CommentGenerator
from bot.models import CommentContext
from bot.settings import settings

router = APIRouter(prefix="/api", tags=["generate"])
store = DataStore()
generator = CommentGenerator()


@router.post("/generate-comment", response_model=GenerateCommentResponse)
def generate_comment(req: GenerateCommentRequest):
    brand = store.get_brand()
    playbook = store.get_playbook(req.subreddit)

    tone = playbook.tone if playbook else "data-driven"
    note = playbook_note(playbook) if playbook else ""

    promo_level = playbook.promo_level if playbook else "none"

    ctx = CommentContext(
        title=req.title[:500],
        subreddit=req.subreddit,
        body=(req.description or "")[: settings.max_post_chars],
        parent_comment=(req.parent_comment or "")[: settings.max_parent_comment_chars]
        or None,
        industry=brand.industry,
        expertise=brand.expertise_summary,
        subreddit_note=note,
        tone=tone,
        promo_level=promo_level,
        product=brand.product,
        company=brand.company,
        competitors=brand.competitors,
        client_name=brand.company,
        max_chars=400,
        min_chars=40,
        max_retries=1,
    )

    try:
        result = generator.from_context(ctx)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    return GenerateCommentResponse(
        comment=result.text,
        ok=result.ok,
        attempts=result.attempts,
        model=result.model,
        reject_reasons=result.reject_reasons,
    )
from typing import Dict

from bot.models import CommentContext, Tone

TONE_HINTS: Dict[Tone, str] = {
    "funny": "One light witty line max. No try-hard jokes.",
    "data-driven": "Lead with a real number or concrete fact. Never invent stats.",
    "direct": "Blunt and useful. Answer in the first sentence.",
}


def build_system_prompt(ctx: CommentContext) -> str:
    note = f"\nr/{ctx.subreddit} note: {ctx.subreddit_note}" if ctx.subreddit_note else ""
    expertise = ""
    if ctx.expertise:
        expertise = f"\nBackground (never mention): {ctx.expertise[:400]}"

    return f"""You write short Reddit comments that sound human and get upvotes.

Rules:
- Answer the post directly. 2-4 sentences. Max {ctx.max_chars} chars.
- No links, CTAs, product mentions, or corporate voice.
- No "Great question", "Hope this helps", "As someone who", hashtags, or sign-offs.
- Tone: {ctx.tone} — {TONE_HINTS[ctx.tone]}{expertise}{note}

Return only the comment."""


def build_user_prompt(ctx: CommentContext) -> str:
    body = ctx.body.strip() or "(empty)"
    lines = [
        f"r/{ctx.subreddit}",
        f"Title: {ctx.title}",
        f"Body: {body}",
    ]
    if ctx.parent_comment:
        lines.append(f"Reply to: {ctx.parent_comment}")
    return "\n".join(lines)
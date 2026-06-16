from typing import Dict

from bot.models import CommentContext, PromoLevel, Tone

TONE_HINTS: Dict[Tone, str] = {
    "funny": "One light witty line max. No try-hard jokes.",
    "data-driven": "Lead with a real number or concrete fact. Never invent stats.",
    "direct": "Blunt and useful. Answer in the first sentence.",
}

PROMO_GUIDANCE: Dict[PromoLevel, str] = {
    "none": "Do NOT mention the product, company, or competitors. Pure value only.",
    "low": (
        "Mention the product only if it directly answers the post. "
        "At most one subtle reference. No links or pitch language."
    ),
    "moderate": (
        "You may reference the product when relevant, but lead with value. "
        "No marketing voice, links, or CTAs."
    ),
}


def build_system_prompt(ctx: CommentContext) -> str:
    note = f"\nr/{ctx.subreddit} note: {ctx.subreddit_note}" if ctx.subreddit_note else ""
    expertise = ""
    if ctx.expertise:
        expertise = f"\nBackground (never mention directly): {ctx.expertise[:400]}"
    if ctx.industry:
        expertise = f"\nYou know {ctx.industry}.{expertise}"

    promo_rules = {
        "none": "- No product mentions, links, CTAs, or corporate voice.",
        "low": "- No links or CTAs. Product mention only if it genuinely fits.",
        "moderate": "- No links or CTAs. No marketing voice.",
    }

    return f"""You write short Reddit comments that sound human and get upvotes.

Rules:
- Answer the post directly. 2-4 sentences. Max {ctx.max_chars} chars.
{promo_rules[ctx.promo_level]}
- No "Great question", "Hope this helps", "As someone who", hashtags, or sign-offs.
- Tone: {ctx.tone} — {TONE_HINTS[ctx.tone]}
- Promo level: {ctx.promo_level} — {PROMO_GUIDANCE[ctx.promo_level]}{expertise}{note}

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

    if ctx.promo_level != "none" or ctx.product or ctx.company or ctx.competitors:
        lines.extend(
            [
                "",
                "Brand context (use only if it naturally fits):",
                f"Product: {ctx.product or '(none)'}",
                f"Company: {ctx.company or '(none)'}",
                f"Competitors: {ctx.competitors or '(none)'}",
            ]
        )

    return "\n".join(lines)
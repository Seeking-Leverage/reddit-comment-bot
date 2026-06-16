from bot.models import CommentContext
from bot.safety import validate_comment


def _ctx(**kwargs) -> CommentContext:
    defaults = {
        "title": "Test",
        "subreddit": "test",
        "body": "body",
        "company": "Acme Corp",
        "product": "Acme Analytics platform",
        "competitors": "RivalCo",
        "min_chars": 10,
        "max_chars": 500,
    }
    defaults.update(kwargs)
    return CommentContext(**defaults)


def test_blocks_company_at_promo_none():
    ok, reasons = validate_comment(
        "Acme Corp has a great approach here.", _ctx(promo_level="none")
    )
    assert not ok
    assert "mentions_company_at_none" in reasons


def test_allows_value_comment_at_promo_none():
    ok, _ = validate_comment(
        "Roughly 30% of teams miss this attribution gap entirely.",
        _ctx(promo_level="none"),
    )
    assert ok


def test_blocks_links_at_promo_low():
    ok, reasons = validate_comment(
        "Try https://example.com for more.", _ctx(promo_level="low")
    )
    assert not ok
    assert any("blocked" in r for r in reasons)
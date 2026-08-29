"""
Reaction toggling.

`Reaction` had a model + admin registration but no service/view/url
anywhere — there was literally no way for a visitor to ever create one.
"""

from weblog.models import Reaction

ALLOWED_EMOJIS = {"👍", "❤️", "🎉", "😮", "😂", "🚀"}


def toggle_reaction(*, article, user, emoji):
    """
    Toggle `emoji` on `article` for `user`.

    Returns (created: bool, reaction_or_none). If the user already reacted
    with this emoji, it's removed (created=False, reaction=None);
    otherwise a new Reaction is created (created=True, reaction=obj).
    """
    if emoji not in ALLOWED_EMOJIS:
        raise ValueError(f"'{emoji}' is not a supported reaction.")

    existing = Reaction.objects.filter(article=article, user=user, emoji=emoji).first()
    if existing:
        existing.delete()
        return False, None

    reaction = Reaction.objects.create(article=article, user=user, emoji=emoji)
    return True, reaction


def reaction_summary(article):
    """
    Returns [{"emoji": "👍", "count": 3}, ...] ordered by popularity —
    used to render a reaction bar without N+1 queries per emoji.
    """
    from django.db.models import Count

    return list(
        Reaction.objects.filter(article=article)
        .values("emoji")
        .annotate(count=Count("id"))
        .order_by("-count")
    )


def user_reactions(article, user):
    """Set of emojis the given user has already used on this article."""
    if not user or not user.is_authenticated:
        return set()
    return set(
        Reaction.objects.filter(article=article, user=user).values_list("emoji", flat=True)
    )

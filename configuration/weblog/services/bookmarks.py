"""
Bookmark toggling — same gap as reactions: model + admin existed, nothing
let a user actually create one.
"""

from weblog.models import Bookmark


def toggle_bookmark(*, article, user):
    """Returns True if now bookmarked, False if it was just removed."""
    bookmark = Bookmark.objects.filter(article=article, user=user).first()
    if bookmark:
        bookmark.delete()
        return False

    Bookmark.objects.create(article=article, user=user)
    return True


def is_bookmarked(article, user):
    if not user or not user.is_authenticated:
        return False
    return Bookmark.objects.filter(article=article, user=user).exists()


def user_bookmarks(user):
    return Bookmark.objects.filter(user=user).select_related("article").order_by("-created_at")

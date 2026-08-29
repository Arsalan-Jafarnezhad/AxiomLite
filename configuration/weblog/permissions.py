from django.core.exceptions import PermissionDenied


def user_can_edit_article(
    user,
    article,
):

    if user.is_superuser:
        return True

    return article.author_id == user.id


def user_can_delete_article(
    user,
    article,
):

    return user_can_edit_article(
        user,
        article,
    )


def require_article_owner(
    user,
    article,
):

    if not user_can_edit_article(
        user,
        article,
    ):
        raise PermissionDenied

def require_comment_owner(user, comment):
    if not comment.author_id == user.id:
        raise PermissionDenied
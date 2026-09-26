from django.db import transaction
from django.utils import timezone

from weblog.models import Comment
from weblog.services.comment_moderation import CommentModerationService

#: Maps a CommentModerationService decision to the resulting comment status.
#: "review" is only ever returned for new comments (see decide_edit(), which
#: never returns it), so an edit can only land on APPROVED or REJECTED.
_MODERATION_STATUS = {
    "approve": Comment.Status.APPROVED,
    "reject": Comment.Status.REJECTED,
    "review": Comment.Status.PENDING,
}


def _apply_moderation(comment, decision, moderation):
    """Stamp a comment with the outcome of an AI moderation pass."""
    comment.status = _MODERATION_STATUS[decision]
    comment.moderated_at = timezone.now()
    comment.moderation_analysis = moderation["raw"]
    comment.moderation_score = moderation["confidence"]

    return comment


@transaction.atomic
def create_comment(
    *,
    article,
    author,
    body,
    parent=None,
):
    """
    Create a comment and run it through AI moderation.

    Laya decides, per its calibrated confidence, whether the comment is
    published immediately, rejected immediately, or held for the
    article's author to verify manually (when Laya isn't confident
    either way — e.g. around 50/50 — or the Laya server is unreachable).
    """
    decision, moderation = CommentModerationService().decide(body)

    comment = Comment.objects.create(
        article=article,
        author=author,
        parent=parent,
        body=body,
    )

    _apply_moderation(comment, decision, moderation)

    comment.save(
        update_fields=[
            "status",
            "moderated_at",
            "moderation_analysis",
            "moderation_score",
        ]
    )

    return comment


@transaction.atomic
def update_comment(
    comment,
    *,
    body,
):
    """
    Update a comment's body and re-run AI moderation on the new text.

    Edits are never sent to the author for manual verification: Laya's
    verdict (publish or reject) is applied directly, whatever its
    confidence.
    """
    decision, moderation = CommentModerationService().decide_edit(body)

    comment.body = body

    _apply_moderation(comment, decision, moderation)

    comment.save()

    return comment


@transaction.atomic
def approve_comment(comment):
    comment.status = Comment.Status.APPROVED

    comment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return comment


@transaction.atomic
def reject_comment(comment):
    comment.status = Comment.Status.REJECTED

    comment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return comment


@transaction.atomic
def mark_comment_pending(comment):
    comment.status = Comment.Status.PENDING

    comment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return comment


@transaction.atomic
def delete_comment(comment):
    """
    Soft-delete a comment.

    The database row is preserved.
    """

    comment.deleted_at = timezone.now()

    comment.save(
        update_fields=[
            "deleted_at",
            "updated_at",
        ]
    )

    return comment


@transaction.atomic
def restore_comment(comment):
    """
    Restore a previously soft-deleted comment.
    """

    comment.deleted_at = None

    comment.save(
        update_fields=[
            "deleted_at",
            "updated_at",
        ]
    )

    return comment


@transaction.atomic
def approve_article_comments(article):
    return (
        Comment.objects.pending()
        .filter(article=article)
        .update(
            status=Comment.Status.APPROVED,
            updated_at=timezone.now(),
        )
    )


@transaction.atomic
def reject_article_comments(article):
    return (
        Comment.objects.pending()
        .filter(article=article)
        .update(
            status=Comment.Status.REJECTED,
            updated_at=timezone.now(),
        )
    )


@transaction.atomic
def delete_article_comments(article):
    """
    Soft-delete every comment belonging to an article.
    """

    now = timezone.now()

    return Comment.objects.filter(
        article=article,
        deleted_at__isnull=True,
    ).update(
        deleted_at=now,
        updated_at=now,
    )

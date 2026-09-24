from django.db import transaction
from django.utils import timezone

from weblog.models import Comment
from weblog.services.comment_moderation import CommentModerationService
from django.utils import timezone

@transaction.atomic
def create_comment(
    *,
    article,
    author,
    body,
    parent=None,
):
    moderation = CommentModerationService().moderate(body)

    comment = Comment.objects.create(
        article=article,
        author=author,
        parent=parent,
        body=body,
        status=(
            Comment.Status.APPROVED
            if moderation["publishable"]
            else Comment.Status.PENDING
        ),
    )
    comment.moderated_at = timezone.now()
    comment.moderation_analysis = moderation["raw"]
    comment.moderation_score = moderation["raw"]["answers"]["is_constructive"]["noul"]
    print(moderation["publishable"])
    comment.save()
    print(comment.moderated_at)
    print(comment.moderation_analysis)
    print(comment.moderation_score)
    
    return comment

@transaction.atomic
def update_comment(
    comment,
    *,
    body,
):
    comment.body = body

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

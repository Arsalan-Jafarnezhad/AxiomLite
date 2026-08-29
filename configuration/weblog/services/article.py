from django.db import transaction
from django.utils import timezone

from weblog.models import (
    Article,
    ArticleView,
)

from weblog.utils.reading_time import reading_time
from weblog.utils.slug import unique_slug


@transaction.atomic
def create_article(
    *,
    author,
    title,
    content,
    **extra_fields,
):
    """
    Create a new article.
    """

    tags = extra_fields.pop(
        "tags",
        None,
    )

    article = Article(
        author=author,
        title=title,
        slug=unique_slug(
            Article,
            title,
        ),
        content=content,
        reading_minutes=reading_time(
            content,
        ),
        **extra_fields,
    )

    article.save()

    if tags is not None:
        article.tags.set(tags)

    return article


@transaction.atomic
def update_article(
    article,
    **data,
):
    """
    Update an existing article.
    """

    tags = data.pop(
        "tags",
        None,
    )

    title = data.get(
        "title",
    )

    if title and title != article.title:

        article.slug = unique_slug(
            Article,
            title,
        )

    for field, value in data.items():

        setattr(
            article,
            field,
            value,
        )

    article.reading_minutes = reading_time(
        article.content,
    )

    article.save()

    if tags is not None:
        article.tags.set(tags)

    return article


@transaction.atomic
def publish_article(
    article,
):
    """
    Publish an article.
    """

    article.status = Article.Status.PUBLISHED

    if article.published_at is None:

        article.published_at = timezone.now()

    article.save(
        update_fields=[
            "status",
            "published_at",
        ]
    )

    return article


@transaction.atomic
def archive_article(
    article,
):
    """
    Archive an article.
    """

    article.status = Article.Status.ARCHIVED

    article.save(
        update_fields=[
            "status",
        ]
    )

    return article


@transaction.atomic
def unpublish_article(
    article,
):
    """
    Move an article back to draft.
    """

    article.status = Article.Status.DRAFT

    article.save(
        update_fields=[
            "status",
        ]
    )

    return article


@transaction.atomic
def schedule_article(
    article,
    publish_at,
):
    """
    Schedule publication.
    """

    article.scheduled_at = publish_at

    article.save(
        update_fields=[
            "scheduled_at",
        ]
    )

    return article


@transaction.atomic
def toggle_featured(
    article,
):
    """
    Toggle featured state.
    """

    article.is_featured = not article.is_featured

    article.save(
        update_fields=[
            "is_featured",
        ]
    )

    return article


@transaction.atomic
def toggle_pinned(
    article,
):
    """
    Toggle pinned state.
    """

    article.is_pinned = not article.is_pinned

    article.save(
        update_fields=[
            "is_pinned",
        ]
    )

    return article


@transaction.atomic
def record_article_view(
    *,
    request,
    article,
):
    """
    Record one unique article view.

    Anonymous:
        session + IP

    Authenticated:
        one record per user
    """

    if request.user.is_authenticated:

        if ArticleView.objects.filter(
            article=article,
            user=request.user,
        ).exists():

            return

        ArticleView.objects.create(
            article=article,
            user=request.user,
            ip_address=get_client_ip(
                request,
            ),
        )

        return

    session_key = f"article-view-{article.pk}"

    if request.session.get(
        session_key,
    ):
        return

    request.session[session_key] = True

    ArticleView.objects.create(
        article=article,
        ip_address=get_client_ip(
            request,
        ),
    )


def get_client_ip(
    request,
):
    """
    Return client's IP address.
    """

    forwarded = request.META.get(
        "HTTP_X_FORWARDED_FOR",
    )

    if forwarded:
        return forwarded.split(
            ",",
            1,
        )[0].strip()

    return request.META.get(
        "REMOTE_ADDR",
    )

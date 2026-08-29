from django import template
from django.utils.html import mark_safe

from weblog.models import Article
from weblog.services.search import latest_articles
from weblog.utils.markdown import render_markdown
from weblog.utils.reading_time import reading_time

register = template.Library()


@register.simple_tag
def article_reading_time(article):
    """
    Return article reading time.
    """

    if hasattr(article, "reading_minutes"):
        return article.reading_minutes

    return reading_time(
        article.content,
    )


@register.simple_tag
def article_views(article):
    """
    Return article views count.
    """

    return article.views_count


@register.simple_tag
def article_comments(article):
    """
    Return approved comments count.
    """

    return article.comments_count


@register.simple_tag
def latest_article_list(limit=5):
    """
    Return latest articles.
    """

    return latest_articles(
        limit=int(limit),
    )


@register.simple_tag
def featured_article_list(limit=5):
    """
    Return featured articles.
    """

    return (
        Article.objects.published()
        .featured()
        .select_related(
            "author",
            "category",
        )[: int(limit)]
    )


@register.filter
def render_article_markdown(content):
    """
    Convert Markdown content to safe HTML.
    """

    if not content:
        return ""

    return mark_safe(
        render_markdown(content),
    )


@register.filter
def truncate_content(
    value,
    length=150,
):
    """
    Simple text truncation.
    """

    if not value:
        return ""

    value = str(value)

    if len(value) <= int(length):
        return value

    return value[: int(length)].rstrip() + "..."


@register.filter
def reading_time_label(minutes):
    """
    Convert minutes to readable text.
    """

    minutes = int(minutes)

    if minutes <= 1:
        return "1 min read"

    return f"{minutes} mins read"


@register.filter
def percentage(value, total):
    """
    Calculate percentage.
    """

    if not total:
        return 0

    return round(
        (value / total) * 100,
        2,
    )

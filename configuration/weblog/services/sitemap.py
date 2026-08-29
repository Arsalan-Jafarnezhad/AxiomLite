from weblog.models import (
    Article,
    Category,
    Tag,
    Series,
)


def article_sitemap_items():
    """
    Return all published articles.
    """

    return Article.objects.published().select_related(
        "author",
        "category",
        "series",
    )


def category_sitemap_items():
    """
    Return all categories.
    """

    return Category.objects.all().order_by(
        "name",
    )


def tag_sitemap_items():
    """
    Return all tags.
    """

    return Tag.objects.all().order_by(
        "name",
    )


def series_sitemap_items():
    """
    Return all series.
    """

    return Series.objects.all().order_by(
        "title",
    )


def article_lastmod(
    article,
):
    """
    Last modification date for an article.
    """

    return article.updated_at or article.published_at


def category_lastmod(
    category,
):
    """
    Last modification date for a category.
    """

    latest = (
        category.articles.published()
        .order_by(
            "-updated_at",
            "-published_at",
        )
        .first()
    )

    if latest:
        return latest.updated_at or latest.published_at

    return None


def tag_lastmod(
    tag,
):
    """
    Last modification date for a tag.
    """

    latest = (
        tag.articles.published()
        .order_by(
            "-updated_at",
            "-published_at",
        )
        .first()
    )

    if latest:
        return latest.updated_at or latest.published_at

    return None


def series_lastmod(
    series,
):
    """
    Last modification date for a series.
    """

    latest = (
        series.articles.published()
        .order_by(
            "-updated_at",
            "-published_at",
        )
        .first()
    )

    if latest:
        return latest.updated_at or latest.published_at

    return None


def article_priority(
    article,
):
    """
    Sitemap priority for articles.
    """

    if article.is_pinned:
        return 1.0

    if article.is_featured:
        return 0.9

    return 0.8


def category_priority(
    category,
):
    return 0.7


def tag_priority(
    tag,
):
    return 0.6


def series_priority(
    series,
):
    return 0.7


def article_changefreq(
    article,
):
    return "weekly"


def category_changefreq(
    category,
):
    return "weekly"


def tag_changefreq(
    tag,
):
    return "weekly"


def series_changefreq(
    series,
):
    return "weekly"

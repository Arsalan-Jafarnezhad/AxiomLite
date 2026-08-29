from django.db.models import Count, Q

from weblog.models import Article


def search_articles(
    query,
):
    """
    Search published articles.
    """

    if not query:
        return Article.objects.none()

    return Article.objects.published().search(query)


def advanced_search(
    *,
    query=None,
    category=None,
    tag=None,
    author=None,
    series=None,
    featured=None,
    pinned=None,
    min_reading_time=None,
    max_reading_time=None,
    ordering="-published_at",
):
    """
    Advanced article search.
    """

    queryset = (
        Article.objects.published()
        .select_related(
            "author",
            "category",
            "series",
        )
        .prefetch_related(
            "tags",
        )
    )

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(subtitle__icontains=query)
            | Q(summary__icontains=query)
            | Q(content__icontains=query)
        )

    if category:
        queryset = queryset.filter(
            category__slug=category,
        )

    if tag:
        queryset = queryset.filter(
            tags__slug=tag,
        )

    if author:
        queryset = queryset.filter(
            author__username=author,
        )

    if series:
        queryset = queryset.filter(
            series__slug=series,
        )

    if featured is not None:
        queryset = queryset.filter(
            is_featured=featured,
        )

    if pinned is not None:
        queryset = queryset.filter(
            is_pinned=pinned,
        )

    if min_reading_time is not None:
        queryset = queryset.filter(
            reading_minutes__gte=min_reading_time,
        )

    if max_reading_time is not None:
        queryset = queryset.filter(
            reading_minutes__lte=max_reading_time,
        )

    return queryset.order_by(
        ordering,
    ).distinct()


def autocomplete(
    query,
    *,
    limit=10,
):
    """
    Autocomplete article titles.
    """

    if not query:
        return []

    return list(
        Article.objects.published()
        .filter(
            title__icontains=query,
        )
        .values_list(
            "title",
            flat=True,
        )[:limit]
    )


def similar_articles(
    article,
    *,
    limit=5,
):
    """
    Find articles similar to another article.
    """

    return (
        Article.objects.published()
        .filter(
            category=article.category,
        )
        .exclude(
            pk=article.pk,
        )
        .select_related(
            "author",
            "category",
        )
        .prefetch_related(
            "tags",
        )
        .order_by(
            "-published_at",
        )[:limit]
    )


def popular_articles(
    *,
    limit=10,
):
    """
    Return most viewed articles.
    """
    return (
        Article.objects.published()
        .annotate(view_count=Count("views", distinct=True))
        .order_by("-view_count", "-published_at")[:limit]
    )


def latest_articles(
    *,
    limit=10,
):
    """
    Return latest published articles.
    """

    return Article.objects.published().order_by(
        "-published_at",
    )[:limit]

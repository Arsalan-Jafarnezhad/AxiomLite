from weblog.models import Series


def series_with_articles(slug):
    """
    Fetch a Series by slug with its articles prefetched.

    Mirrors `category_with_articles` / `tag_with_articles` — this module
    was missing entirely, which broke `SeriesDetailView` with an
    ImportError the moment the urlconf loaded.
    """
    return Series.objects.prefetch_related("articles").get(slug=slug)


def series_list():
    return Series.objects.all()

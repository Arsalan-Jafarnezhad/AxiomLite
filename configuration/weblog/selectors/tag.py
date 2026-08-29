from weblog.models import Tag


def tag_with_articles(slug):
    """Fetch a Tag by slug with its articles prefetched."""
    return Tag.objects.prefetch_related("articles").get(slug=slug)


def tags():
    return Tag.objects.all()

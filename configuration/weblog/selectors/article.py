from django.db.models import Count, Q

from weblog.models import Article


def article_list():

    return (
        Article.objects
        .published()
        .public()
        .select_related(
            "author",
            "category",
            "series",
        )
        .prefetch_related("tags")
    )
# def article_detail(slug):

#     return (
#         Article.objects.published()
#         .select_related(
#             "author",
#             "category",
#             "series",
#         )
#         .prefetch_related(
#             "tags",
#             "media",
#         )
#         .annotate(comments_count=Count("comments"))
#         .get(slug=slug)
#     )




def article_detail(slug):
    return (
        Article.objects.published()
        .select_related(
            "author",
            "category",
            "series",
        )
        .prefetch_related(
            "tags",
        )
        .annotate(
            approved_comments_count=Count(
                "comments",
                filter=Q(comments__status="approved"),
            )
        )
        .get(slug=slug)
    )


def featured_articles():

    return (
        Article.objects.published()
        .featured()
        .select_related(
            "author",
            "category",
        )
    )


def pinned_articles():

    return Article.objects.all().published().pinned()


def articles_by_author(username):

    return (
        Article.objects
        # .published()
        .filter(author__username=username).select_related("author")
    )


def search_articles(query):

    return (
        Article.objects.all()
        # .published()
        # .search(query)
    )


def related_articles(article, limit=5):

    return (
        Article.objects
        # .published()
        .filter(category=article.category).exclude(id=article.id)[:limit]
    )

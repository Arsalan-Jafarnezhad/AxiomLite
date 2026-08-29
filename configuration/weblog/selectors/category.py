from weblog.models import Category



def get_category(
    slug
):

    return (
        Category.objects
        .prefetch_related(
            "articles"
        )
        .get(
            slug=slug
        )
    )



def categories():

    return (
        Category.objects
        .order_by(
            "name"
        )
    )



def category_with_articles(
    slug
):

    return (
        Category.objects
        .prefetch_related(
            "articles"
        )
        .get(
            slug=slug
        )
    )
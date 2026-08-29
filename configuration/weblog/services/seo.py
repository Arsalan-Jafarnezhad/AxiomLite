from django.utils.html import strip_tags

from weblog.models import ArticleSEO

DEFAULT_DESCRIPTION_LENGTH = 160
DEFAULT_TITLE_LENGTH = 60


def generate_meta_title(
    article,
):
    """
    Generate an SEO-friendly meta title.
    """

    if hasattr(article, "seo") and article.seo.meta_title:
        return article.seo.meta_title

    title = article.title.strip()

    if len(title) <= DEFAULT_TITLE_LENGTH:
        return title

    return title[: DEFAULT_TITLE_LENGTH - 3].rstrip() + "..."


def generate_meta_description(
    article,
):
    """
    Generate an SEO-friendly meta description.
    """

    if hasattr(article, "seo") and article.seo.meta_description:
        return article.seo.meta_description

    text = article.summary or article.content

    text = strip_tags(text).strip()

    if len(text) <= DEFAULT_DESCRIPTION_LENGTH:
        return text

    return text[: DEFAULT_DESCRIPTION_LENGTH - 3].rstrip() + "..."


def get_canonical_url(
    article,
    request=None,
):
    """
    Return canonical URL.
    """

    if hasattr(article, "seo") and article.seo.canonical_url:
        return article.seo.canonical_url

    if request is not None:
        return request.build_absolute_uri(article.get_absolute_url())

    return article.get_absolute_url()


def get_open_graph_data(
    article,
    request=None,
):
    """
    Return Open Graph metadata.
    """

    image = None

    if article.cover:
        if request:
            image = request.build_absolute_uri(article.cover.url)
        else:
            image = article.cover.url

    return {
        "title": generate_meta_title(article),
        "description": generate_meta_description(article),
        "url": get_canonical_url(
            article,
            request,
        ),
        "image": image,
        "type": "article",
    }


def get_twitter_card_data(
    article,
    request=None,
):
    """
    Return Twitter Card metadata.
    """

    data = get_open_graph_data(
        article,
        request,
    )

    data["card"] = "summary_large_image" if data["image"] else "summary"

    return data


def update_seo(
    article,
    *,
    meta_title=None,
    meta_description=None,
    canonical_url=None,
):
    """
    Create or update an article SEO object.
    """

    seo, _ = ArticleSEO.objects.get_or_create(
        article=article,
    )

    if meta_title is not None:
        seo.meta_title = meta_title

    if meta_description is not None:
        seo.meta_description = meta_description

    if canonical_url is not None:
        seo.canonical_url = canonical_url

    seo.save()

    return seo

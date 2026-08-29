from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.utils.feedgenerator import Rss201rev2Feed

from weblog.models import Article


class LatestArticlesFeed(Feed):
    """
    RSS feed for the latest published articles.
    """

    feed_type = Rss201rev2Feed

    title = "Latest Articles"

    link = "/rss/"

    description = "Latest published articles."

    language = "en"

    def items(self):
        return (
            Article.objects.published()
            .select_related(
                "author",
                "category",
            )
            .order_by(
                "-published_at",
            )[:20]
        )

    def item_title(
        self,
        item,
    ):
        return item.title

    def item_description(
        self,
        item,
    ):
        return item.summary or truncatewords(
            item.content,
            50,
        )

    def item_link(
        self,
        item,
    ):
        return item.get_absolute_url()

    def item_author_name(
        self,
        item,
    ):
        return item.author.get_full_name() or item.author.username

    def item_pubdate(
        self,
        item,
    ):
        return item.published_at

    def item_categories(
        self,
        item,
    ):
        categories = []

        if item.category:
            categories.append(
                item.category.name,
            )

        categories.extend(
            item.tags.values_list(
                "name",
                flat=True,
            )
        )

        return categories


class CategoryFeed(Feed):
    """
    RSS feed for a single category.
    """

    feed_type = Rss201rev2Feed

    def get_object(
        self,
        request,
        slug,
    ):
        from weblog.models import Category

        return Category.objects.get(
            slug=slug,
        )

    def title(
        self,
        obj,
    ):
        return f"{obj.name} Articles"

    def link(
        self,
        obj,
    ):
        return obj.get_absolute_url()

    def description(
        self,
        obj,
    ):
        return obj.description or obj.name

    def items(
        self,
        obj,
    ):
        return (
            Article.objects.published()
            .filter(
                category=obj,
            )
            .select_related(
                "author",
                "category",
            )
            .order_by(
                "-published_at",
            )[:20]
        )

    def item_title(
        self,
        item,
    ):
        return item.title

    def item_description(
        self,
        item,
    ):
        return item.summary or truncatewords(
            item.content,
            50,
        )

    def item_link(
        self,
        item,
    ):
        return item.get_absolute_url()

    def item_pubdate(
        self,
        item,
    ):
        return item.published_at

"""
XML sitemap endpoint.

The previous version redefined four `Sitemap` subclasses *inside*
`SitemapView.get()`, rebuilding them from scratch on every single request,
and hardcoded flat `priority`/`changefreq` values while the smarter,
per-object `article_priority()` / `article_changefreq()` etc. helpers in
`services/sitemap.py` sat completely unused. Moved to module level and
wired up to actually use them.
"""

from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.views import View

from weblog.services.sitemap import (
    article_changefreq,
    article_lastmod,
    article_priority,
    article_sitemap_items,
    category_changefreq,
    category_lastmod,
    category_priority,
    category_sitemap_items,
    series_changefreq,
    series_lastmod,
    series_priority,
    series_sitemap_items,
    tag_changefreq,
    tag_lastmod,
    tag_priority,
    tag_sitemap_items,
)


class ArticleSitemap(Sitemap):
    def items(self):
        return article_sitemap_items()

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return article_lastmod(obj)

    def priority(self, obj):
        return article_priority(obj)

    def changefreq(self, obj):
        return article_changefreq(obj)


class CategorySitemap(Sitemap):
    def items(self):
        return category_sitemap_items()

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return category_lastmod(obj)

    def priority(self, obj):
        return category_priority(obj)

    def changefreq(self, obj):
        return category_changefreq(obj)


class TagSitemap(Sitemap):
    def items(self):
        return tag_sitemap_items()

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return tag_lastmod(obj)

    def priority(self, obj):
        return tag_priority(obj)

    def changefreq(self, obj):
        return tag_changefreq(obj)


class SeriesSitemap(Sitemap):
    def items(self):
        return series_sitemap_items()

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return series_lastmod(obj)

    def priority(self, obj):
        return series_priority(obj)

    def changefreq(self, obj):
        return series_changefreq(obj)


SITEMAPS = {
    "articles": ArticleSitemap(),
    "categories": CategorySitemap(),
    "tags": TagSitemap(),
    "series": SeriesSitemap(),
}


class SitemapView(View):
    """XML sitemap endpoint."""

    def get(self, request, *args, **kwargs):
        return sitemap(request, sitemaps=SITEMAPS)

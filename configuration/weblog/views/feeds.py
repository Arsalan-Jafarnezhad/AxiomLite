"""
Thin re-export layer so `weblog.urls.feeds` has stable class names to wire
up, without views importing straight from `services` (keeps the
services/views layering the rest of the app already uses).

The previous version of this module defined `latest_feed()` / `category_feed()`
as plain functions with the wrong signatures (`latest_feed()` took no
`request` argument at all) while `urls/feeds.py` actually referenced a
third, nonexistent name (`feeds.ArticleFeed`) — an AttributeError that
crashed the whole urlconf on import.
"""

from weblog.services.rss import CategoryFeed, LatestArticlesFeed

__all__ = ["LatestArticlesFeed", "CategoryFeed"]

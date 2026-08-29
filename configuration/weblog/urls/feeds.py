from django.urls import path

from weblog.views.feeds import CategoryFeed, LatestArticlesFeed

urlpatterns = [
    path("rss/", LatestArticlesFeed(), name="rss"),
    path("rss/category/<slug:slug>/", CategoryFeed(), name="rss-category"),
]

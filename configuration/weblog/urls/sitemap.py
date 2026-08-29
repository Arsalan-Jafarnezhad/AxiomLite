from django.urls import path

from weblog.views.sitemap import SitemapView

urlpatterns = [
    path("sitemap.xml", SitemapView.as_view(), name="sitemap"),
]

from django.urls import path

from weblog.views import public

urlpatterns = [
    path(
        "",
        public.WeblogIndexView.as_view(),
        name="index",
    ),

    path(
        "articles/",
        public.ArticleListView.as_view(),
        name="articles",
    ),
    path("article/<slug:slug>/", public.ArticleDetailView.as_view(), name="article-detail"),
    path("category/<slug:slug>/", public.CategoryArticleListView.as_view(), name="category"),
    path("tag/<slug:slug>/", public.TagArticleListView.as_view(), name="tag"),
    path("series/<slug:slug>/", public.SeriesDetailView.as_view(), name="series"),
    path("author/<str:username>/", public.AuthorArticleListView.as_view(), name="author"),
    path("archive/", public.ArchiveListView.as_view(), name="archive"),
]

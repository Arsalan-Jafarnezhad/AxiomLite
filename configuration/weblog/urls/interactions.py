from django.urls import path

from weblog.views.interactions import BookmarkToggleView, ReactionToggleView

urlpatterns = [
    path("article/<slug:slug>/react/", ReactionToggleView.as_view(), name="article-react"),
    path("article/<slug:slug>/bookmark/", BookmarkToggleView.as_view(), name="article-bookmark"),
]

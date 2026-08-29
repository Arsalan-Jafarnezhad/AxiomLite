from django.urls import path

from weblog.views import dashboard

app_name = "dashboard"

urlpatterns = [
    path("", dashboard.DashboardView.as_view(), name="index"),
    path("articles/", dashboard.ArticleListView.as_view(), name="articles"),
    path("articles/create/", dashboard.ArticleCreateView.as_view(), name="article-create"),
    path("articles/<int:pk>/edit/", dashboard.ArticleUpdateView.as_view(), name="article-update"),
    path("articles/<int:pk>/delete/", dashboard.ArticleDeleteView.as_view(), name="article-delete"),
    path("comments/", dashboard.CommentListView.as_view(), name="comments"),
]

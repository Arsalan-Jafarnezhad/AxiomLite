from django.urls import path

from weblog.views.search import SearchView

urlpatterns = [
    path("search/", SearchView.as_view(), name="search"),
]

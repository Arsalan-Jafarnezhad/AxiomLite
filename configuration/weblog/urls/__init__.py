"""
weblog/urls/__init__.py

Mounted from the project root as e.g.:

    path("blog/", include("weblog.urls")),

`app_name = "weblog"` here is what actually establishes the "weblog:" url
namespace — the previous version concatenated raw `urlpatterns` lists from
each sub-module (`public_urls + dashboard_urls + ...`) without ever
declaring `app_name`, and `dashboard.py`'s own `app_name = "dashboard"` was
silently discarded in the process (only its `urlpatterns` list was
imported). The result: every `reverse("weblog:...")` /
`reverse("weblog:dashboard:...")` call in the codebase was reversing
against namespaces that didn't actually exist.
"""

from django.urls import include, path

app_name = "weblog"

urlpatterns = [
    path("", include("weblog.urls.public")),
    path("", include("weblog.urls.search")),
    path("", include("weblog.urls.comment")),
    path("", include("weblog.urls.interactions")),
    path("", include("weblog.urls.feeds")),
    path("", include("weblog.urls.sitemap")),
    path("", include("weblog.urls.api")),
    path("dashboard/", include(("weblog.urls.dashboard", "weblog"), namespace="dashboard")),
]

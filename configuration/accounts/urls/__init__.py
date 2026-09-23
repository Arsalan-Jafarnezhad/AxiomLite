"""URL configuration for the accounts application."""

from django.urls import include, path

app_name = "accounts"

urlpatterns = [
    path("", include("accounts.urls.authentication")),
    path("", include("accounts.urls.account")),
    path("", include("accounts.urls.profile")),
    path("", include("accounts.urls.api")),
]
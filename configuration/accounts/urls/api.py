"""API URL configuration for the accounts application."""

from django.urls import include, path

# app_name = "api"

urlpatterns = [
    path("api/", include("accounts.api.urls")),
]
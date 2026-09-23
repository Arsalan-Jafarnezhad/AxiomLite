"""Authenticated account URLs."""

from django.urls import path

from accounts.views.account import (
    AccountDetailView,
    AccountEditView,
    AccountView,
    IndexView,
)

urlpatterns = [
    path(
        "",
        IndexView.as_view(),
        name="index",
    ),
    path(
        "account/",
        AccountView.as_view(),
        name="account",
    ),
    path(
        "account/edit/",
        AccountEditView.as_view(),
        name="account-edit",
    ),
    path(
        "account/detail/",
        AccountDetailView.as_view(),
        name="account-detail",
    ),
]
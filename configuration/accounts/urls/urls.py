from django.urls import path

from . import views
from django.views.generic import RedirectView

app_name = "accounts"


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "sign-in/",
        views.SignInView.as_view(),
        name="sign-in",
    ),
    # path(
    #     "login/",
    #     RedirectView.as_view("accounts:sign-in"),
    #     name="login-redirect",
    # ),
    # path(
    #     "logout/",
    #     RedirectView.as_view("accounts:sign-out"),
    #     name="logout-redirect",
    # ),
    path(
        "sign-up/",
        views.SignUpView.as_view(),
        name="sign-up",
    ),
    path(
        "sign-out/",
        views.SignOutView.as_view(),
        name="sign-out",
    ),
    path(
        "account/",
        views.AccountView.as_view(),
        name="account",
    ),
    path(
        "account/edit/",
        views.AccountEditView.as_view(),
        name="account-edit",
    ),
    path(
        "account/detail/",
        views.AccountDetailView.as_view(),
        name="account-detail",
    ),
    path(
        "profiles/<str:username>/",
        views.ProfileView.as_view(),
        name="profile",
    ),
]

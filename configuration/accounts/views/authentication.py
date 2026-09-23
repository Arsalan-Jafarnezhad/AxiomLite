"""Authentication-related views."""

from typing import Any

from allauth.account.views import LoginView
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.forms.authentication import (
    AccountLoginForm,
    AccountSignUpForm,
)

User = get_user_model()


class SignInView(LoginView):
    """Handle user sign-in."""

    template_name = "accounts/authentication/sign-in.html"
    redirect_authenticated_user = True
    form_class = AccountLoginForm

    def get_success_url(self) -> str:
        """Return the URL after successful authentication."""
        return str(reverse_lazy("core:index"))

    def form_invalid(self, form: Any) -> HttpResponse:
        """Display a generic authentication error."""
        messages.error(
            self.request,
            "Invalid email or password.",
        )
        return super().form_invalid(form)


class SignUpView(CreateView):
    """Register a new user and authenticate them."""

    form_class = AccountSignUpForm
    template_name = "accounts/authentication/sign-up.html"
    success_url = reverse_lazy("core:index")

    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        """Prevent authenticated users from accessing registration."""
        if request.user.is_authenticated:
            return redirect(reverse_lazy("core:index"))

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def form_valid(
        self,
        form: AccountSignUpForm,
    ) -> HttpResponse:
        """Create the account and authenticate the new user."""
        response = super().form_valid(form)

        login(
            self.request,
            self.object,
        )

        messages.success(
            self.request,
            "Your account has been created successfully.",
        )

        return response

    def form_invalid(
        self,
        form: AccountSignUpForm,
    ) -> HttpResponse:
        """Display a registration validation message."""
        messages.error(
            self.request,
            "Please correct the errors below.",
        )
        return super().form_invalid(form)


class SignOutView(APIView):
    """Log out the current user."""

    permission_classes = [AllowAny]

    def post(
        self,
        request: Request,
    ) -> Response:
        """Log out the current session."""
        username = request.user.get_username()

        logout(request)

        return Response(
            {
                "level": "success",
                "message": (
                    f"Goodbye, {username}. "
                    "You've been signed out."
                ),
            },
            status=status.HTTP_200_OK,
        )
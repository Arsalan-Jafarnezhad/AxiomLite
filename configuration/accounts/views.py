from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.base import RedirectView

from allauth.account.views import LoginView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import AccountForm, AccountLoginForm, AccountSignUpForm, ProfileForm

User = get_user_model()


class IndexView(RedirectView):
    """`/` inside this app just forwards to the account dashboard."""

    pattern_name = "accounts:account"


class SignInView(LoginView):
    template_name = "accounts/authentication/sign-in.html"
    redirect_authenticated_user = True
    form_class = AccountLoginForm

    def get_success_url(self) -> str:
        return str(reverse_lazy("core:index"))

    def form_invalid(self, form: Any) -> HttpResponse:
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)


class SignUpView(CreateView):
    """Registers a new user (custom email-first form) and logs them in."""

    form_class = AccountSignUpForm
    template_name = "accounts/authentication/sign-up.html"
    success_url = reverse_lazy("core:index")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(reverse_lazy("core:index"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: AccountSignUpForm) -> HttpResponse:
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Your account has been created successfully.")
        return response

    def form_invalid(self, form: AccountSignUpForm) -> HttpResponse:
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class SignOutView(APIView):
    """Logs out the current user; consumed by an AJAX call from the header."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        username = request.user.get_username()
        logout(request)
        return Response(
            {
                "level": "success",
                "message": f"Goodbye, {username}. You've been signed out.",
            },
            status=status.HTTP_200_OK,
        )


class AccountView(LoginRequiredMixin, TemplateView):
    """Private dashboard for the logged-in user's own account."""

    template_name = "accounts/account/account.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["has_usable_password"] = user.has_usable_password()
        ctx["is_email_verified"] = user.is_email_verified
        ctx["is_phone_number_verified"] = user.is_phone_number_verified
        return ctx


class AccountEditView(LoginRequiredMixin, UpdateView):
    """Edits the logged-in user's account info + profile in a single form post."""

    model = User
    form_class = AccountForm
    template_name = "accounts/account/edit.html"
    success_url = reverse_lazy("accounts:account-edit")

    def get_object(self, queryset=None) -> User:
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            ctx["profile_form"] = ProfileForm(
                self.request.POST,
                self.request.FILES,
                instance=self.request.user.profile,
            )
        else:
            ctx["profile_form"] = ProfileForm(instance=self.request.user.profile)
        return ctx

    def form_valid(self, form: AccountForm) -> HttpResponse:
        profile_form = self.get_context_data()["profile_form"]
        if not profile_form.is_valid():
            return self.form_invalid(form)

        self.object = form.save()
        profile_form.save()
        messages.success(self.request, "Your account has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form: AccountForm) -> HttpResponse:
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class AccountDetailView(LoginRequiredMixin, DetailView):
    """
    Read-only detailed information about the authenticated user's account.
    """

    model = User
    template_name = "accounts/account/detail.html"
    context_object_name = "account_user"

    def get_object(self, queryset=None) -> User:
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)

        user = self.request.user
        profile = user.profile

        ctx.update(
            {
                "profile": profile,
                # Account/security
                "has_usable_password": user.has_usable_password(),
                "is_email_verified": user.is_email_verified,
                "is_phone_number_verified": user.is_phone_number_verified,
                # Permissions
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )

        return ctx


class ProfileView(DetailView):
    """
    Public profile page for any user, looked up by username.

    Renders a minimal "secure" template instead of the full profile when
    the owner has locked their profile down.
    """

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get_object(self, queryset=None) -> User:
        user = User.objects.get_by_username(self.kwargs[self.slug_url_kwarg])
        if user is None:
            raise Http404("User not found.")
        return user

    def get(self, request, *args, **kwargs):
        # Cache the object once so get_template_names()/get_context_data()
        # don't each re-fetch it (and re-trigger update_level()).
        self.object = self.get_object()
        self.object.profile.update_level()
        return self.render_to_response(self.get_context_data(object=self.object))

    def get_template_names(self) -> list[str]:
        if self.object.profile.is_private:
            return ["accounts/profile/secure.html"]
        return ["accounts/profile/public.html"]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["is_own_profile"] = self.request.user == self.object
        return ctx

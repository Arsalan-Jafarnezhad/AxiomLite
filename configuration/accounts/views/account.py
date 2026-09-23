"""Authenticated user's account views."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, RedirectView, TemplateView, UpdateView

from accounts.forms.account import AccountForm
from accounts.forms.profile import ProfileForm

User = get_user_model()


class IndexView(RedirectView):
    """Redirect the accounts root to the account dashboard."""

    pattern_name = "accounts:account"


class AccountView(LoginRequiredMixin, TemplateView):
    """Display the authenticated user's account dashboard."""

    template_name = "accounts/account/account.html"

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Add account security information to the context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update(
            {
                "has_usable_password": user.has_usable_password(),
                "is_email_verified": user.is_email_verified,
                "is_phone_number_verified": (
                    user.is_phone_number_verified
                ),
            }
        )

        return context


class AccountEditView(LoginRequiredMixin, UpdateView):
    """Edit the authenticated user's account and profile."""

    model = User
    form_class = AccountForm
    template_name = "accounts/account/edit.html"
    success_url = reverse_lazy("accounts:account-edit")

    def get_object(self, queryset=None):
        """Return the currently authenticated user."""
        return self.request.user

    def get_profile_form(self):
        """Return the profile form for the current request."""
        return ProfileForm(
            self.request.POST or None,
            self.request.FILES or None,
            instance=self.request.user.profile,
        )

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Add the profile form to the template context."""
        context = super().get_context_data(**kwargs)

        context["profile_form"] = kwargs.get(
            "profile_form",
            self.get_profile_form(),
        )

        return context

    def form_valid(
        self,
        form: AccountForm,
    ) -> HttpResponse:
        """Validate and save both account and profile forms."""
        profile_form = self.get_profile_form()

        if not profile_form.is_valid():
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    profile_form=profile_form,
                )
            )

        self.object = form.save()
        profile_form.save()

        messages.success(
            self.request,
            "Your account has been updated successfully.",
        )

        return redirect(self.get_success_url())

    def form_invalid(
        self,
        form: AccountForm,
    ) -> HttpResponse:
        """Render the account form with validation errors."""
        messages.error(
            self.request,
            "Please correct the errors below.",
        )

        return self.render_to_response(
            self.get_context_data(
                form=form,
                profile_form=self.get_profile_form(),
            )
        )


class AccountDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about the current account."""

    model = User
    template_name = "accounts/account/detail.html"
    context_object_name = "account_user"

    def get_object(self, queryset=None):
        """Return the currently authenticated user."""
        return self.request.user

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Add profile and security information to the context."""
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context.update(
            {
                "profile": user.profile,
                "has_usable_password": user.has_usable_password(),
                "is_email_verified": user.is_email_verified,
                "is_phone_number_verified": (
                    user.is_phone_number_verified
                ),
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )

        return context
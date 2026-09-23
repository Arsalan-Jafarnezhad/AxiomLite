"""Forms for editing authenticated-user account information."""

from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

INPUT_CLASS = (
    "input input-bordered w-full rounded-xl pl-10 "
    "focus:input-primary transition-all duration-200"
)


class AccountForm(forms.ModelForm):
    """Form for editing the authenticated user's account information."""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "gender",
            "born_date",
            "phone_number",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "last_name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "email": forms.EmailInput(attrs={"class": INPUT_CLASS}),
            "username": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "gender": forms.Select(attrs={"class": INPUT_CLASS}),
            "born_date": forms.DateInput(
                attrs={
                    "class": INPUT_CLASS,
                    "type": "date",
                }
            ),
            "phone_number": forms.TextInput(attrs={"class": INPUT_CLASS}),
        }

    def clean_email(self) -> str:
        """Normalize the email and reject another user's email."""
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")

        return email

    def clean_username(self) -> str:
        """Normalize and validate username uniqueness."""
        username = self.cleaned_data["username"].strip()

        if not username:
            return username

        if (
            User.objects.filter(username__iexact=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError("This username is already in use.")

        return username

    @property
    def fieldsets(self) -> list[dict[str, Any]]:
        """Return fields grouped for the project's form renderer."""
        return [
            {
                "name": "Personal Information",
                "fields": [
                    self["first_name"],
                    self["last_name"],
                    self["gender"],
                    self["born_date"],
                ],
            },
            {
                "name": "Account Information",
                "fields": [
                    self["username"],
                    self["phone_number"],
                    self["email"],
                ],
            },
        ]

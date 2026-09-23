"""Authentication forms for the accounts application."""

from typing import Any

from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

User = get_user_model()

INPUT_CLASS = (
    "input input-bordered w-full rounded-xl pl-10 "
    "focus:input-primary transition-all duration-200"
)
CHECKBOX_CLASS = "toggle toggle-primary"


class AccountLoginForm(LoginForm):
    """Django-allauth login form styled for the project's UI."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields["login"].label = "Email Address"
        self.fields["login"].widget = forms.EmailInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Enter your email address",
                "autocomplete": "email",
                "autofocus": True,
                "id": "login-email",
            }
        )

        self.fields["password"].label = "Password"
        self.fields["password"].widget = forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS + " pr-16",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
                "id": "login-password",
            }
        )

        if "remember" in self.fields:
            self.fields["remember"].label = "Keep me signed in"
            self.fields["remember"].widget = forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASS,
                    "id": "remember-me",
                }
            )

    @property
    def fieldsets(self) -> list[dict[str, Any]]:
        """Return fields grouped for the Unfold form renderer."""
        sections = [
            {
                "name": None,
                "fields": [
                    self["login"],
                    self["password"],
                ],
            }
        ]

        if "remember" in self.fields:
            sections.append(
                {
                    "name": None,
                    "fields": [self["remember"]],
                }
            )

        return sections


class AccountSignUpForm(forms.ModelForm):
    """Registration form for the custom email-first user model."""

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "autocomplete": "new-password",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "autocomplete": "email",
                    "autofocus": True,
                }
            ),
        }

    def clean_email(self) -> str:
        """Normalize the email and reject an existing account."""
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.email_exists(email):
            raise ValidationError("This email is already registered.")

        return email

    def clean_password2(self) -> str:
        """Ensure both password fields contain the same value."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        return password2

    def clean(self) -> dict[str, Any]:
        """Run Django's configured password validators."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password2")

        if password:
            password_validation.validate_password(
                password,
                self.instance,
            )

        return cleaned_data

    def save(self, commit: bool = True) -> User:
        """Create the user with a properly hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user

"""Forms for authentication and account/profile management (DaisyUI-styled)."""

from typing import Any

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from allauth.account.forms import LoginForm

from accounts.models.profile import Profile

User = get_user_model()

INPUT_CLASS = (
    "input input-bordered w-full rounded-xl pl-10 "
    "focus:input-primary transition-all duration-200"
)
CHECKBOX_CLASS = "toggle toggle-primary"
FILE_INPUT_CLASS = "file-input file-input-bordered w-full rounded-xl"
TEXTAREA_CLASS = "textarea textarea-bordered w-full rounded-xl"


class AccountLoginForm(LoginForm):
    """django-allauth login form, restyled for DaisyUI."""

    def __init__(self, *args: Any, **kwargs: Any):
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
                attrs={"class": CHECKBOX_CLASS, "id": "remember-me"}
            )

    @property
    def fieldsets(self):
        sections = [{"name": None, "fields": [self["login"], self["password"]]}]
        if "remember" in self.fields:
            sections.append({"name": None, "fields": [self["remember"]]})
        return sections


class AccountSignUpForm(forms.ModelForm):
    """Registration form for the custom, email-first ``User`` model."""

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": INPUT_CLASS, "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": INPUT_CLASS, "autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": INPUT_CLASS, "autocomplete": "email", "autofocus": True}
            ),
        }

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    def clean(self) -> dict:
        cleaned = super().clean()
        password = cleaned.get("password2")
        if password:
            password_validation.validate_password(password, self.instance)
        return cleaned

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AccountForm(forms.ModelForm):
    """Edits the logged-in user's own account info (used by AccountEditView)."""

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
            "born_date": forms.DateInput(attrs={"class": INPUT_CLASS, "type": "date"}),
            "phone_number": forms.TextInput(attrs={"class": INPUT_CLASS}),
        }

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email

    @property
    def fieldsets(self):
        return [
            {
                "name": "Personal Information",
                "fields": [self["first_name"], self["last_name"], self["gender"], self["born_date"]],
            },
            {
                "name": "Account Information",
                "fields": [self["username"], self["phone_number"], self["email"]],
            },
        ]


class ProfileForm(forms.ModelForm):
    """Edits the public-facing Profile fields alongside AccountForm."""

    class Meta:
        model = Profile
        fields = ("avatar", "display_name", "biography", "is_private")
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class": FILE_INPUT_CLASS}),
            "display_name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "biography": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "is_private": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
        }

    @property
    def fieldsets(self):
        return [
            {
                "name": "Profile Information",
                "fields": [self["avatar"], self["display_name"], self["biography"], self["is_private"]],
            },
        ]

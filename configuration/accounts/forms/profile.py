"""Forms for editing public user profiles."""

from typing import Any

from django import forms

from accounts.models import Profile

INPUT_CLASS = (
    "input input-bordered w-full rounded-xl pl-10 "
    "focus:input-primary transition-all duration-200"
)
CHECKBOX_CLASS = "toggle toggle-primary"
FILE_INPUT_CLASS = "file-input file-input-bordered " "w-full rounded-xl"
TEXTAREA_CLASS = "textarea textarea-bordered " "w-full rounded-xl"


class ProfileForm(forms.ModelForm):
    """Form for editing public-facing profile information."""

    class Meta:
        model = Profile
        fields = (
            "avatar",
            "display_name",
            "biography",
            "is_private",
        )
        widgets = {
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": FILE_INPUT_CLASS,
                }
            ),
            "display_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                }
            ),
            "biography": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 4,
                }
            ),
            "is_private": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASS,
                }
            ),
        }

    @property
    def fieldsets(self) -> list[dict[str, Any]]:
        """Return fields grouped for the project's form renderer."""
        return [
            {
                "name": "Profile Information",
                "fields": [
                    self["avatar"],
                    self["display_name"],
                    self["biography"],
                    self["is_private"],
                ],
            },
        ]

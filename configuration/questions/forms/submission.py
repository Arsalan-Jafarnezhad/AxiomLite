from django import forms
from questions.models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["code"]
        widgets = {
            "code": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full font-mono min-h-96",
                "spellcheck": "false",
                "autocomplete": "off",
            })
        }

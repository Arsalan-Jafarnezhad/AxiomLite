from django import forms
from questions.widgets import QuestionMarkdownWidget
from questions.models import Question, TestCase

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title","slug","description","difficulty","language","tags","status","evaluation_type","evaluator","created_by","is_featured","sort_order","published_at"]
        widgets = {"description": QuestionMarkdownWidget(attrs={"rows": 28})}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("evaluation_type") == "automatic" and self.instance.pk:
            if not self.instance.test_cases.filter(is_active=True).exists() and cleaned.get("status") == "published":
                raise forms.ValidationError("Automatic questions need at least one active test before publication.")
        return cleaned

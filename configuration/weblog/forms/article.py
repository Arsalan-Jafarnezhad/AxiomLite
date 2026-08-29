from django import forms

from weblog.models import Article
from weblog.widgets.markdown import MarkdownWidget

class ArticleForm(forms.ModelForm):

    class Meta:

        model = Article

        fields = [
            "title",
            "subtitle",
            "category",
            "series",
            "tags",
            "summary",
            "slug",
            "content",
            "cover",
            "status",
            "visibility",
            "allow_comments",
            "is_featured",
            "is_pinned",
            "published_at",
            "scheduled_at",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Article title",
                }
            ),

            "subtitle": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Article subtitle",
                }
            ),

            "summary": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 3,
                    "placeholder": "Short description",
                }
            ),

            "content": MarkdownWidget(
                attrs={
                    "rows": 25,
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "select select-bordered w-full",
                }
            ),

            "series": forms.Select(
                attrs={
                    "class": "select select-bordered w-full",
                }
            ),

            "tags": forms.SelectMultiple(
                attrs={
                    "class": "select select-bordered w-full",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "select select-bordered w-full",
                }
            ),

            "visibility": forms.Select(
                attrs={
                    "class": "select select-bordered w-full",
                }
            ),

            # "published_at": forms.DateTimeInput(
            #     attrs={
            #         "class": "input input-bordered w-full",
            #         "type": "datetime-local",
            #     }
            # ),

            # "scheduled_at": forms.DateTimeInput(
            #     attrs={
            #         "class": "input input-bordered w-full",
            #         "type": "datetime-local",
            #     }
            # ),
        }


    def clean_title(self):

        title = self.cleaned_data["title"].strip()

        if len(title) < 5:
            raise forms.ValidationError(
                "Title must be at least 5 characters."
            )

        return title

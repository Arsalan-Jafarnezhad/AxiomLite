from django import forms
from django.urls import reverse


class MarkdownWidget(forms.Textarea):

    template_name = "weblog/widgets/markdown.html"

    class Media:
        css = {"all": ("styles/weblog/markdown-editor.css",)}

        js = ("scripts/weblog/markdown-editor.js",)

    def get_context(
        self,
        name,
        value,
        attrs=None,
    ):
        context = super().get_context(
            name,
            value,
            attrs,
        )

        context["upload_url"] = reverse("weblog:articles-upload-image")

        return context

    def __init__(self, attrs=None):
        attrs = attrs or {}

        attrs.setdefault(
            "rows",
            20,
        )

        # attrs.setdefault(
        #     "placeholder",
        #     "Write your article in Markdown...",
        # )

        super().__init__(
            attrs=attrs,
        )

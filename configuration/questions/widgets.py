from django import forms
from django.urls import reverse

class QuestionMarkdownWidget(forms.Textarea):
    template_name = "questions/widgets/markdown.html"
    class Media:
        css={"all":("styles/weblog/markdown-editor.css",)}
        js=("scripts/weblog/markdown-editor.js",)
    def get_context(self,name,value,attrs=None):
        context=super().get_context(name,value,attrs)
        context["upload_url"]=reverse("weblog:articles-upload-image")
        return context
    def __init__(self,attrs=None):
        attrs=attrs or {}
        attrs.setdefault("rows",28)
        super().__init__(attrs=attrs)

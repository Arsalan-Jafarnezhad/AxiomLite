from django import forms

from weblog.models import Comment


class CommentForm(forms.ModelForm):

    class Meta:

        model = Comment

        fields = [
            "body",
        ]

        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": ("textarea " "textarea-bordered " "w-full " "min-h-32"),
                    "placeholder": ("Share your thoughts..."),
                    "maxlength": 2000,
                }
            )
        }

    def __init__(
        self,
        *args,
        user=None,
        article=None,
        parent=None,
        **kwargs,
    ):

        super().__init__(
            *args,
            **kwargs,
        )

        self.user = user
        self.article = article
        self.parent = parent

    def clean_body(self):

        body = self.cleaned_data["body"].strip()

        if not body:
            raise forms.ValidationError("Comment cannot be empty.")

        if len(body) > 2000:
            raise forms.ValidationError("Comments cannot exceed 2000 characters.")

        return body

    def save(
        self,
        commit=True,
    ):

        comment = super().save(
            commit=False,
        )

        comment.author = self.user
        comment.article = self.article
        comment.parent = self.parent

        if commit:
            comment.save()

        return comment

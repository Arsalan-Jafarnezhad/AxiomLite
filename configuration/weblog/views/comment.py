from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import UpdateView

from weblog.forms.comment import CommentForm
from weblog.models import Article, Comment
from weblog.permissions import require_comment_owner
from weblog.services.comments import (
    approve_comment,
    create_comment,
    delete_comment,
    reject_comment,
    update_comment,
)


class CommentCreateView(
    LoginRequiredMixin,
    View,
):

    form_class = CommentForm

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):

        article = get_object_or_404(
            Article.objects.published(),
            pk=request.POST.get("article"),
        )

        if not article.allow_comments:
            messages.error(
                request,
                "Comments are disabled for this article.",
            )

            return redirect(article.get_absolute_url())

        parent = None

        parent_id = request.POST.get(
            "parent",
        )

        if parent_id:

            parent = get_object_or_404(
                Comment.objects.approved(),
                pk=parent_id,
                article=article,
            )

        form = self.form_class(
            request.POST,
            user=request.user,
            article=article,
            parent=parent,
        )

        if not form.is_valid():

            messages.error(
                request,
                "Please correct the errors below.",
            )

            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    article.get_absolute_url(),
                )
            )

        comment = create_comment(
            article=article,
            author=request.user,
            body=form.cleaned_data["body"],
            parent=parent,
        )

        messages.success(
            request,
            ("Your comment has been submitted " "for moderation."),
        )

        return redirect(article.get_absolute_url() + "#comments")


class CommentUpdateView(
    LoginRequiredMixin,
    UpdateView,
):

    model = Comment

    form_class = CommentForm

    template_name = "weblog/comment_form.html"

    context_object_name = "comment"

    def dispatch(
        self,
        request,
        *args,
        **kwargs,
    ):

        self.object = self.get_object()

        require_comment_owner(
            request.user,
            self.object,
        )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs.update(
            {
                "user": self.request.user,
                "article": self.object.article,
                "parent": self.object.parent,
            }
        )

        return kwargs

    def form_valid(
        self,
        form,
    ):

        update_comment(
            self.object,
            body=form.cleaned_data["body"],
        )

        messages.success(
            self.request,
            "Comment updated.",
        )

        return redirect(self.object.article.get_absolute_url() + "#comments")


class CommentDeleteView(
    LoginRequiredMixin,
    View,
):

    def post(
        self,
        request,
        pk,
    ):

        comment = get_object_or_404(
            Comment,
            pk=pk,
        )

        if comment.article.author != request.user and not request.user.is_staff:
            raise Http404

        delete_comment(
            comment,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Comment deleted successfully.",
                "comment_id": comment.pk,
            }
        )


class CommentApproveView(
    LoginRequiredMixin,
    View,
):

    def post(
        self,
        request,
        pk,
    ):

        comment = get_object_or_404(
            Comment,
            pk=pk,
        )

        if comment.article.author != request.user and not request.user.is_staff:
            raise Http404

        approve_comment(
            comment,
        )

        return JsonResponse(
            {
                "success": True,
                "status": comment.status,
                "sentiment": comment.sentiment_label,
                "sentiment_score": comment.sentiment_score,
            }
        )


class CommentRejectView(
    LoginRequiredMixin,
    View,
):

    def post(
        self,
        request,
        pk,
    ):

        comment = get_object_or_404(
            Comment,
            pk=pk,
        )

        if comment.article.author != request.user and not request.user.is_staff:
            raise Http404

        reject_comment(
            comment,
        )

        return JsonResponse(
            {
                "success": True,
                "status": comment.status,
                "sentiment": comment.sentiment_label,
                "sentiment_score": comment.sentiment_score,
            }
        )

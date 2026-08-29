from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import Comment


@admin.register(Comment)
class CommentAdmin(ModelAdmin):

    list_display = (
        "article",
        "author",
        "status",
        "sentiment_label",
        "sentiment_score",
        "created_at",
    )

    list_filter = (
        "status",
        "sentiment_label",
        "created_at",
    )

    search_fields = (
        "body",
        "author__username",
        "article__title",
    )

    autocomplete_fields = (
        "article",
        "author",
        "parent",
    )

    readonly_fields = ("created_at",)

    actions = (
        "approve_comments",
        "reject_comments",
    )

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        queryset.update(status=Comment.Status.APPROVED)

    @admin.action(description="Reject selected comments")
    def reject_comments(self, request, queryset):
        queryset.update(status=Comment.Status.REJECTED)

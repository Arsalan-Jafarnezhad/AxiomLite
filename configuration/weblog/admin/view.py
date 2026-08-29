from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import ArticleView


@admin.register(ArticleView)
class ArticleViewAdmin(ModelAdmin):

    list_display = (
        "article",
        "user",
        "ip_address",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "article__title",
        "user__username",
        "ip_address",
    )

    readonly_fields = (
        "created_at",
    )
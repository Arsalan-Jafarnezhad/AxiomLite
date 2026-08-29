from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(ModelAdmin):

    list_display = (
        "user",
        "article",
        "created_at",
    )

    search_fields = (
        "user__username",
        "article__title",
    )

    autocomplete_fields = (
        "user",
        "article",
    )

    readonly_fields = (
        "created_at",
    )
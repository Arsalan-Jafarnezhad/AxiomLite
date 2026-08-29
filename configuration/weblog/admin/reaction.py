from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import Reaction


@admin.register(Reaction)
class ReactionAdmin(ModelAdmin):

    list_display = (
        "article",
        "user",
        "emoji",
        "created_at",
    )

    list_filter = (
        "emoji",
    )

    search_fields = (
        "article__title",
        "user__username",
    )

    autocomplete_fields = (
        "article",
        "user",
    )
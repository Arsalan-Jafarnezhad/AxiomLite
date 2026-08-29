from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import Media


@admin.register(Media)
class MediaAdmin(ModelAdmin):

    list_display = (
        "article",
        "file",
        "uploaded_at",
    )

    search_fields = (
        "article__title",
        "caption",
    )

    autocomplete_fields = (
        "article",
    )

    readonly_fields = (
        "uploaded_at",
    )
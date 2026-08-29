from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import Tag


@admin.register(Tag)
class TagAdmin(ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": (
            "name",
        )
    }
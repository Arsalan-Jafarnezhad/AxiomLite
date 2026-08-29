from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import Series


@admin.register(Series)
class SeriesAdmin(ModelAdmin):

    list_display = (
        "title",
        "slug",
    )

    search_fields = (
        "title",
        "description",
    )

    prepopulated_fields = {
        "slug": (
            "title",
        )
    }
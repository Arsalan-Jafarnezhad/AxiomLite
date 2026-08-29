from unfold.admin import ModelAdmin
from django.contrib import admin

from weblog.models import Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin):

    list_display = (
        "name",
        "slug",
        "created_at",
    )

    search_fields = (
        "name",
    )

    readonly_fields = (
        "slug",
        "created_at",
    )

    prepopulated_fields = {
        "slug": (
            "name",
        )
    }
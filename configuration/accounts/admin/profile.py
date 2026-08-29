from django.contrib import admin
from unfold.admin import ModelAdmin

from accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = (
        "name",
        "user",
        "points",
        "level",
        "created_at",
    )

    search_fields = (
        "display_name",
        "user__email",
        "user__username",
    )

    list_filter = (
        "level",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "user",
    )
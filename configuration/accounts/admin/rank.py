from django.contrib import admin
from unfold.admin import ModelAdmin

from accounts.models import Rank


@admin.register(Rank)
class RankAdmin(ModelAdmin):
    list_display = (
        "name",
        "activation_level",
        "priority",
    )

    list_filter = (
        "activation_level",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "-priority",
    )
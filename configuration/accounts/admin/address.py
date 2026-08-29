from django.contrib import admin
from unfold.admin import ModelAdmin

from accounts.models import Address


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    list_display = (
        "title",
        "user",
        "city",
        "country",
        "is_default",
    )

    list_filter = (
        "country",
        "city",
        "is_default",
    )

    search_fields = (
        "title",
        "user__email",
        "receiver_name",
        "postal_code",
    )

    autocomplete_fields = (
        "user",
    )
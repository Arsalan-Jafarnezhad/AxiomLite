from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin

from accounts.models import Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    can_delete = False

@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    ordering = ["-date_joined"]

    list_display = (
        "email",
        "username",
        "full_name",
        "is_verified",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "is_verified",
        "is_staff",
        "is_active",
        "gender",
        "date_joined",
    )

    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "public_id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "date_joined",
        "last_login",
        "email_verified_at",
        "phone_number_verified_at",
    )

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                )
            },
        ),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "born_date",
                    "gender",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    "is_verified",
                    "email_verified_at",
                    "phone_number_verified_at",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Activity",
            {
                "fields": (
                    "last_login",
                    "last_login_ip",
                    "last_login_country",
                    "last_activity_at",
                )
            },
        ),
        (
            "System",
            {
                "fields": (
                    # "public_id",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    
    inlines = [
        ProfileInline,
    ]
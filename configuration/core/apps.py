from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    # def ready(self):
    #     """Initialize application services."""
    #     from .services import laya  # noqa: F401
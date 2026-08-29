from django.contrib import admin
from unfold.admin import ModelAdmin

from weblog.models import ArticleSEO


@admin.register(ArticleSEO)
class ArticleSEOAdmin(ModelAdmin):

    list_display = (
        "article",
        "meta_title",
    )

    search_fields = (
        "article__title",
        "meta_title",
    )

    autocomplete_fields = (
        "article",
    )
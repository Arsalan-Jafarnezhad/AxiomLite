from django.contrib import admin

from unfold.admin import ModelAdmin

from weblog.models import Article
from weblog.models import Media, ArticleSEO
from weblog.forms.article import ArticleForm

class MediaInline(admin.TabularInline):
    model = Media
    extra = 0


class SEOInline(admin.StackedInline):
    model = ArticleSEO
    extra = 0


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    form = ArticleForm
    list_display = (
        "title",
        "author",
        "status",
        "visibility",
        "category",
        "reading_minutes",
        "published_at",
        "created_at",
    )


    list_filter = (
        "status",
        "visibility",
        "category",
        "is_featured",
        "is_pinned",
        "created_at",
        "published_at",
    )


    search_fields = (
        "title",
        "subtitle",
        "summary",
        "content",
        "author__username",
    )


    autocomplete_fields = (
        "author",
        "category",
        "series",
        "tags",
    )


    readonly_fields = (
        # "slug",
        "reading_minutes",
        "created_at",
        "updated_at",
    )


    list_per_page = 30


    prepopulated_fields = {
        "slug": (
            "title",
        )
    }


    inlines = [
        SEOInline,
        MediaInline,
    ]


    fieldsets = (

        (
            "Main Information",
            {
                "fields": (
                    "title",
                    "subtitle",
                    "slug",
                    "summary",
                    "content",
                    "cover",
                )
            }
        ),


        (
            "Organization",
            {
                "fields": (
                    "author",
                    "category",
                    "series",
                    "tags",
                )
            }
        ),


        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "visibility",
                    "published_at",
                    "scheduled_at",
                )
            }
        ),


        (
            "Options",
            {
                "fields": (
                    "allow_comments",
                    "is_featured",
                    "is_pinned",
                    "reading_minutes",
                )
            }
        ),

    )
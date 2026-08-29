from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from weblog.forms.comment import CommentForm
from weblog.models import Article, Category, Series, Tag
from weblog.selectors.article import (
    article_detail,
    article_list,
    featured_articles,
    pinned_articles,
    related_articles,
)
from weblog.selectors.category import categories, category_with_articles
from weblog.selectors.series import series_with_articles
from weblog.selectors.tag import tag_with_articles
from weblog.services.article import record_article_view
from weblog.services.bookmarks import is_bookmarked
from weblog.services.reactions import reaction_summary, user_reactions
from weblog.services.search import popular_articles
from weblog.selectors.comment import (
    article_comments,
    article_sentiment_summary,
)

User = get_user_model()


class WeblogIndexView(ListView):
    """
    Weblog landing page.

    The landing page introduces the Weblog and highlights
    featured, pinned, popular, and latest content without
    becoming the full article listing page.
    """

    template_name = "weblog/index.html"
    context_object_name = "popular_articles"

    def get_queryset(self):
        return popular_articles(limit=6)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            featured_articles=featured_articles()[:3],
            pinned_articles=pinned_articles()[:3],
            latest_articles=article_list()[:3],
            categories=categories(),
            total_articles=Article.objects.published().count(),
        )

        return context


class ArticleListView(ListView):
    """
    Full public article listing.

    Displays published articles with pagination and search.
    """

    template_name = "weblog/article/list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return article_list()

    def get_paginate_by(self, queryset):
        """Allow custom page size via ?page_size=N, capped at 50."""
        try:
            page_size = int(self.request.GET.get("page_size", self.paginate_by))
        except (TypeError, ValueError):
            page_size = self.paginate_by
        return max(1, min(page_size, 50))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            total_articles=self.get_queryset().count(),
        )

        return context


class ArticleDetailView(DetailView):
    """
    Public article page.

    Features:
    - Published articles only
    - Related articles
    - Approved comments
    - Comment form
    - Previous/next navigation
    - Sentiment summary
    - Reaction summary
    - Bookmark state
    - Unique view recording
    """

    model = Article
    template_name = "weblog/article/detail.html"
    context_object_name = "article"

    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        try:
            return article_detail(self.kwargs.get(self.slug_url_kwarg))
        except Article.DoesNotExist:
            raise Http404("Article not found.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        context.update(
            comments=article_comments(article),
            # All sentiment calculations are performed
            # inside the selector.
            sentiment_summary=article_sentiment_summary(article),
            related_articles=related_articles(article),
            comment_form=CommentForm(),
            previous_article=(
                Article.objects.published()
                .filter(
                    published_at__lt=article.published_at,
                )
                .order_by("-published_at")
                .first()
            ),
            next_article=(
                Article.objects.published()
                .filter(
                    published_at__gt=article.published_at,
                )
                .order_by("published_at")
                .first()
            ),
            reaction_summary=reaction_summary(article),
            user_reactions=user_reactions(
                article,
                self.request.user,
            ),
            is_bookmarked=is_bookmarked(
                article,
                self.request.user,
            ),
        )

        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        record_article_view(
            request=request,
            article=self.object,
        )

        return response


class CategoryArticleListView(ListView):
    """Published articles belonging to a category."""

    template_name = "weblog/category.html"
    context_object_name = "articles"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        try:
            self.category = category_with_articles(kwargs.get("slug"))
        except Category.DoesNotExist:
            # NOTE: the original code wrote `except self.category.DoesNotExist`
            # here, which itself raised AttributeError before `self.category`
            # was ever assigned — masking every real 404 with a 500.
            raise Http404("Category not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return article_list().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            category=self.category, total_articles=self.get_queryset().count()
        )
        return context


class TagArticleListView(ListView):
    """Published articles for a tag."""

    template_name = "weblog/tag.html"
    context_object_name = "articles"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        try:
            self.tag = tag_with_articles(kwargs["slug"])
        except Tag.DoesNotExist:
            raise Http404("Tag not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return article_list().filter(tags=self.tag).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(tag=self.tag, total_articles=self.get_queryset().count())
        return context


class SeriesDetailView(ListView):
    """Published articles in a series."""

    template_name = "weblog/series.html"
    context_object_name = "articles"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        try:
            self.series = series_with_articles(kwargs["slug"])
        except Series.DoesNotExist:
            raise Http404("Series not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return article_list().filter(series=self.series)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(series=self.series, total_articles=self.get_queryset().count())
        return context


class AuthorArticleListView(ListView):
    """Published articles by an author."""

    template_name = "weblog/author.html"
    context_object_name = "articles"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.author = get_object_or_404(User, username=kwargs["username"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return article_list().filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            author=self.author,
            total_articles=self.get_queryset().count(),
            featured_articles=article_list().filter(
                author=self.author, is_featured=True
            )[:5],
        )
        return context


class ArchiveListView(ListView):
    """All published articles in reverse chronological order."""

    template_name = "weblog/archive.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return article_list()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["archive_title"] = "Archive"
        return context

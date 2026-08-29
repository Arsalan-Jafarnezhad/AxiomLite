from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from weblog.forms.article import ArticleForm
from weblog.models import Article, Comment
from weblog.permissions import require_article_owner
from weblog.services.article import (
    create_article,
    update_article,
)


class DashboardView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Dashboard homepage.
    """

    template_name = "weblog/dashboard/index.html"

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs,
        )

        articles = Article.objects.all()
        #     .by_author(
        #     self.request.user,
        # )

        context.update(
            total_articles=articles.count(),
            # published_articles=(articles.published().count()),
            # draft_articles=(articles.drafts().count()),
            # review_articles=(articles.review().count()),
            # archived_articles=(articles.archived().count()),
            published_articles=(articles.all().count()),
            draft_articles=(articles.all().count()),
            review_articles=(articles.all().count()),
            archived_articles=(articles.all().count()),
            total_comments=(
                Comment.objects.filter(
                    article__author=self.request.user,
                ).count()
            ),
            latest_articles=(articles[:10]),
        )

        return context


class ArticleListView(
    LoginRequiredMixin,
    ListView,
):
    """
    User articles.
    """

    model = Article

    template_name = "weblog/dashboard/article/list.html"

    context_object_name = "articles"

    paginate_by = 20

    def get_queryset(
        self,
    ):
        return (
            Article.objects
            # .by_author(
            #     self.request.user,
            # )
            .select_related(
                "category",
                "series",
            ).prefetch_related(
                "tags",
            )
        )


class ArticleCreateView(
    LoginRequiredMixin,
    CreateView,
):
    """
    Create article.
    """

    model = Article

    form_class = ArticleForm

    template_name = "weblog/dashboard/article/form.html"

    def form_valid(
        self,
        form,
    ):
        form.instance.author = self.request.user

        response = super().form_valid(
            form,
        )

        messages.success(
            self.request,
            "Article created successfully.",
        )

        return response

    def get_success_url(
        self,
    ):
        return reverse_lazy(
            "weblog:dashboard:article-update",
            kwargs={
                "pk": self.object.pk,
            },
        )


class ArticleUpdateView(
    LoginRequiredMixin,
    UpdateView,
):
    """
    Update article.
    """

    model = Article

    form_class = ArticleForm

    template_name = "weblog/dashboard/article/form.html"

    def dispatch(
        self,
        request,
        *args,
        **kwargs,
    ):

        self.object = self.get_object()

        require_article_owner(
            request.user,
            self.object,
        )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def form_valid(
        self,
        form,
    ):

        update_article(
            self.object,
            **form.cleaned_data,
        )

        messages.success(
            self.request,
            "Article updated successfully.",
        )

        return super().form_valid(
            form,
        )

    def get_success_url(
        self,
    ):
        return reverse_lazy(
            "weblog:dashboard:article-update",
            kwargs={
                "pk": self.object.pk,
            },
        )


class ArticleDeleteView(
    LoginRequiredMixin,
    DeleteView,
):
    """
    Delete article.
    """

    model = Article

    template_name = "weblog/dashboard/article_confirm_delete.html"

    success_url = reverse_lazy(
        "weblog:dashboard:articles",
    )

    def dispatch(
        self,
        request,
        *args,
        **kwargs,
    ):

        require_article_owner(
            request.user,
            self.get_object(),
        )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )


class CommentListView(
    LoginRequiredMixin,
    ListView,
):
    """
    List non-deleted comments on the user's articles.
    """

    model = Comment

    template_name = "weblog/dashboard/comment/list.html"

    context_object_name = "comments"

    paginate_by = 20

    def get_queryset(
        self,
    ):
        return (
            Comment.objects.not_deleted()
            .filter(
                article__author=self.request.user,
            )
            .select_related(
                "author",
                "article",
            )
            .recent()
        )

# weblog/tests/factories.py

import factory
from django.contrib.auth import get_user_model

from weblog.models import (
    Article,
    Category,
    Tag,
    Series,
    Comment,
    ArticleView,
    ArticleSEO,
    Media,
)

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")

    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

    password = factory.PostGenerationMethodCall(
        "set_password",
        "password123",
    )


class CategoryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")

    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class TagFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"Tag {n}")

    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class SeriesFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Series

    title = factory.Sequence(lambda n: f"Series {n}")

    slug = factory.LazyAttribute(lambda obj: obj.title.lower().replace(" ", "-"))


class ArticleFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Article

    author = factory.SubFactory(
        UserFactory,
    )

    category = factory.SubFactory(
        CategoryFactory,
    )

    series = factory.SubFactory(
        SeriesFactory,
    )

    title = factory.Sequence(lambda n: f"Article {n}")

    subtitle = "Article subtitle"

    summary = "Article summary"

    content = (
        "This is article content. "
        "It contains enough words "
        "for testing reading time."
    )

    status = Article.Status.PUBLISHED

    visibility = Article.Visibility.PUBLIC

    @factory.post_generation
    def tags(
        self,
        create,
        extracted,
        **kwargs,
    ):

        if not create:
            return

        if extracted:

            for tag in extracted:
                self.tags.add(tag)


class CommentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Comment

    article = factory.SubFactory(
        ArticleFactory,
    )

    author = factory.SubFactory(
        UserFactory,
    )

    body = "This is a test comment."

    status = Comment.Status.APPROVED


class ArticleViewFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ArticleView

    article = factory.SubFactory(
        ArticleFactory,
    )

    user = factory.SubFactory(
        UserFactory,
    )

    ip_address = "127.0.0.1"


class ArticleSEOFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ArticleSEO

    article = factory.SubFactory(
        ArticleFactory,
    )

    meta_title = "SEO title"

    meta_description = "SEO description"

    canonical_url = "https://example.com/article/"


class MediaFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Media

    article = factory.SubFactory(
        ArticleFactory,
    )

    title = "Media title"

    file = "test/image.jpg"

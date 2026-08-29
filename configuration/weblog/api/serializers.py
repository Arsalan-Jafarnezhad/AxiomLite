from rest_framework import serializers

from weblog.models import (
    Article,
    Bookmark,
    Category,
    Comment,
    Reaction,
    Series,
    Tag,
)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "slug",
        ]


class SeriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Series
        fields = [
            "id",
            "title",
            "slug",
        ]


class ArticleListSerializer(serializers.ModelSerializer):

    author = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    category = CategorySerializer(
        read_only=True,
    )

    class Meta:
        model = Article

        fields = [
            "id",
            "title",
            "subtitle",
            "slug",
            "summary",
            "cover",
            "author",
            "category",
            "reading_minutes",
            "published_at",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):

    author = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    category = CategorySerializer(
        read_only=True,
    )

    tags = TagSerializer(
        many=True,
        read_only=True,
    )

    series = SeriesSerializer(
        read_only=True,
    )

    views_count = serializers.IntegerField(
        read_only=True,
    )

    comments_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Article

        fields = [
            "id",
            "title",
            "subtitle",
            "slug",
            "summary",
            "content",
            "cover",
            "author",
            "category",
            "tags",
            "series",
            "reading_minutes",
            "views_count",
            "comments_count",
            "published_at",
        ]


class ArticleImageUploadSerializer(serializers.Serializer):

    image = serializers.ImageField(
        required=True,
    )

    def validate_image(self, image):

        if image.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image is too large. Maximum size is 10 MB."
            )

        return image


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = Comment

        fields = [
            "id",
            "article",
            "author",
            "parent",
            "body",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "status",
            "author",
            "created_at",
        ]


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment

        fields = [
            "article",
            "body",
            "parent",
        ]


class ReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reaction

        fields = [
            "id",
            "article",
            "user",
            "emoji",
            "created_at",
        ]

        read_only_fields = [
            "user",
            "created_at",
        ]


class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark

        fields = [
            "id",
            "article",
            "user",
            "created_at",
        ]

        read_only_fields = [
            "user",
            "created_at",
        ]

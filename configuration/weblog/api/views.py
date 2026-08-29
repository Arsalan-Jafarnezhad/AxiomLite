from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from weblog.models import Article
from weblog.models import Bookmark
from weblog.models import Comment
from weblog.models import Reaction
from weblog.services.image_upload import save_article_image

from .filters import ArticleFilter
from .pagination import ArticlePagination
from .permissions import IsAuthenticatedOrReadOnly
from .serializers import ArticleDetailSerializer
from .serializers import ArticleImageUploadSerializer
from .serializers import ArticleListSerializer
from .serializers import BookmarkSerializer
from .serializers import CommentCreateSerializer
from .serializers import CommentSerializer
from .serializers import ReactionSerializer


class ArticleViewSet(ReadOnlyModelViewSet):

    lookup_field = "slug"

    pagination_class = ArticlePagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ArticleFilter

    search_fields = [
        "title",
        "summary",
        "content",
    ]

    ordering_fields = [
        "published_at",
        "reading_minutes",
    ]

    ordering = [
        "-published_at",
    ]

    def get_queryset(self):

        return (
            Article.objects.published()
            .select_related(
                "author",
                "category",
                "series",
            )
            .prefetch_related(
                "tags",
            )
        )

    def get_serializer_class(self):

        if self.action == "list":
            return ArticleListSerializer

        if self.action == "upload_image":
            return ArticleImageUploadSerializer

        return ArticleDetailSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="upload-image",
        parser_classes=[
            MultiPartParser,
            FormParser,
        ],
        permission_classes=[
            permissions.IsAuthenticated,
        ],
    )
    def upload_image(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        image = serializer.validated_data["image"]

        url = save_article_image(image)

        return Response(
            {
                "url": url,
            },
            status=status.HTTP_201_CREATED,
        )


class CommentViewSet(ModelViewSet):

    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):

        return (
            Comment.objects.approved()
            .select_related(
                "author",
                "article",
            )
            .prefetch_related(
                "replies",
            )
        )

    def get_serializer_class(self):

        if self.action == "create":
            return CommentCreateSerializer

        return CommentSerializer

    def perform_create(
        self,
        serializer,
    ):

        serializer.save(
            author=self.request.user,
        )


class ReactionViewSet(ModelViewSet):
    """
    Authenticated users manage only their own reactions.
    """

    serializer_class = ReactionSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):

        return Reaction.objects.filter(
            user=self.request.user,
        ).select_related(
            "article",
        )

    def perform_create(
        self,
        serializer,
    ):

        serializer.save(
            user=self.request.user,
        )


class BookmarkViewSet(ModelViewSet):
    """
    Authenticated users manage only their own bookmarks.
    """

    serializer_class = BookmarkSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):

        return Bookmark.objects.filter(
            user=self.request.user,
        ).select_related(
            "article",
        )

    def perform_create(
        self,
        serializer,
    ):

        serializer.save(
            user=self.request.user,
        )

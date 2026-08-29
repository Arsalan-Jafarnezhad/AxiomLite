from rest_framework.routers import DefaultRouter

from .views import (
    ArticleViewSet,
    BookmarkViewSet,
    CommentViewSet,
    ReactionViewSet,
)

router = DefaultRouter()

router.register(
    "articles",
    ArticleViewSet,
    basename="articles",
)

router.register(
    "comments",
    CommentViewSet,
    basename="comments",
)

router.register(
    "reactions",
    ReactionViewSet,
    basename="reactions",
)

router.register(
    "bookmarks",
    BookmarkViewSet,
    basename="bookmarks",
)


urlpatterns = router.urls

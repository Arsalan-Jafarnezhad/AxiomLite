from django.urls import path

from weblog.views import comment

urlpatterns = [
    path(
        "comments/create/",
        comment.CommentCreateView.as_view(),
        name="comment-create",
    ),
    path(
        "comments/<int:pk>/edit/",
        comment.CommentUpdateView.as_view(),
        name="comment-update",
    ),
    path(
        "comments/<int:pk>/delete/",
        comment.CommentDeleteView.as_view(),
        name="comment-delete",
    ),
    path(
        "comments/<int:pk>/approve/",
        comment.CommentApproveView.as_view(),
        name="comment-approve",
    ),
    path(
        "comments/<int:pk>/reject/",
        comment.CommentRejectView.as_view(),
        name="comment-reject",
    ),
]

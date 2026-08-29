from django.urls import path
from questions.views.submission import SubmissionDetailView, SubmissionListView

urlpatterns = [
    path("", SubmissionListView.as_view(), name="submission-list"),
    path("<int:pk>/", SubmissionDetailView.as_view(), name="submission-detail"),
]

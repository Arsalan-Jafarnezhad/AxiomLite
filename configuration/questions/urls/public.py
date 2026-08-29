from django.urls import path
from questions.views.public import QuestionListView, QuestionDetailView
from questions.views.submission import SubmitSolutionView

urlpatterns = [
    path("", QuestionListView.as_view(), name="list"),
    path("<slug:slug>/", QuestionDetailView.as_view(), name="detail"),
    path("<slug:slug>/submit/", SubmitSolutionView.as_view(), name="submit"),
]

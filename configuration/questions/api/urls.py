from django.urls import path
from questions.api.views import QuestionListAPIView,QuestionDetailAPIView,QuestionSubmissionCreateAPIView,SubmissionListAPIView,SubmissionDetailAPIView
urlpatterns=[
 path("questions/",QuestionListAPIView.as_view(),name="question-list"),
 path("questions/<slug:slug>/",QuestionDetailAPIView.as_view(),name="question-detail"),
 path("questions/<slug:slug>/submissions/",QuestionSubmissionCreateAPIView.as_view(),name="question-submit"),
 path("submissions/",SubmissionListAPIView.as_view(),name="submission-list"),
 path("submissions/<int:pk>/",SubmissionDetailAPIView.as_view(),name="submission-detail"),
]

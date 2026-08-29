from django.db.models import Max
from rest_framework import generics, permissions
from rest_framework.response import Response
from questions.models import Question, Submission
from questions.selectors.questions import published_questions, annotate_user_status
from questions.selectors.submissions import submission_for_user
from questions.api.serializers import QuestionListSerializer, QuestionDetailSerializer, SubmissionCreateSerializer, SubmissionSerializer
from questions.services.submission import create_submission

class QuestionListAPIView(generics.ListAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class=QuestionListSerializer
    def get_queryset(self):
        qs=annotate_user_status(published_questions(),self.request.user)
        q=self.request.query_params.get("q")
        difficulty=self.request.query_params.get("difficulty")
        language=self.request.query_params.get("language")
        tag=self.request.query_params.get("tag")
        if q: qs=qs.search(q)
        if difficulty: qs=qs.filter(difficulty=difficulty)
        if language: qs=qs.filter(language__slug=language)
        if tag: qs=qs.filter(tags__slug=tag)
        return qs

class QuestionDetailAPIView(generics.RetrieveAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class=QuestionDetailSerializer
    lookup_field="slug"
    queryset=published_questions()

class QuestionSubmissionCreateAPIView(generics.CreateAPIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=SubmissionCreateSerializer
    def create(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question=__import__("django.shortcuts",fromlist=["get_object_or_404"]).get_object_or_404(Question.objects.published(),slug=kwargs["slug"])
        submission=create_submission(user=request.user,question=question,code=serializer.validated_data["code"])
        return Response(SubmissionSerializer(submission,context={"request":request}).data,status=201)

class SubmissionListAPIView(generics.ListAPIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=SubmissionSerializer
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).select_related("question","language").prefetch_related("test_results")

class SubmissionDetailAPIView(generics.RetrieveAPIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=SubmissionSerializer
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).select_related("question","language").prefetch_related("test_results")

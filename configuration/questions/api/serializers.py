from rest_framework import serializers
from questions.models import Question, Language, Tag, Submission, TestResult

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Language
        fields=["id","name","slug","code"]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tag
        fields=["id","name","slug"]

class QuestionListSerializer(serializers.ModelSerializer):
    language=LanguageSerializer(read_only=True)
    tags=TagSerializer(many=True,read_only=True)
    user_status=serializers.SerializerMethodField()
    best_score=serializers.SerializerMethodField()
    class Meta:
        model=Question
        fields=["id","title","slug","difficulty","language","tags","is_featured","user_status","best_score"]
    def get_user_status(self,obj):
        if not self.context["request"].user.is_authenticated: return "not_attempted"
        if getattr(obj,"has_solved",False): return "solved"
        if getattr(obj,"has_attempted",False): return "attempted"
        return "not_attempted"
    def get_best_score(self,obj):
        u=self.context["request"].user
        if not u.is_authenticated: return None
        return obj.submissions.filter(user=u).order_by("-final_score").values_list("final_score",flat=True).first()

class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model=TestResult
        fields=["id","test_order","status","passed","actual_output","error_type","error_message","execution_time"]

class SubmissionSerializer(serializers.ModelSerializer):
    test_results=TestResultSerializer(many=True,read_only=True)
    question_slug=serializers.CharField(source="question.slug",read_only=True)
    class Meta:
        model=Submission
        fields=["id","question_slug","status","automatic_score","manual_score","final_score","passed_tests_count","failed_tests_count","total_tests_count","created_at","started_at","finished_at","execution_time","error_type","error_message","manual_feedback","code","test_results"]
        read_only_fields=[f for f in fields if f not in {"code"}]

class SubmissionCreateSerializer(serializers.Serializer):
    code=serializers.CharField(allow_blank=True)

class QuestionDetailSerializer(QuestionListSerializer):
    description = serializers.SerializerMethodField()
    class Meta(QuestionListSerializer.Meta):
        fields = QuestionListSerializer.Meta.fields + ["description","evaluation_type","evaluator"]
    def get_description(self,obj):
        from questions.services.markdown import render_question_markdown
        return render_question_markdown(obj.description)

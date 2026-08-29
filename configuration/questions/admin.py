from django.contrib import admin
from unfold.admin import ModelAdmin
from questions.models import Question, Language, Tag, TestCase, Submission, TestResult
from questions.forms.question import QuestionForm

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 0
    fields = ("order","name","is_active","is_hidden","timeout","comparison_mode","inputs","expected_outputs")

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    form = QuestionForm
    list_display = ("title","difficulty","language","evaluation_type","evaluator","status","is_featured","created_at")
    list_filter = ("status","difficulty","evaluation_type","language","is_featured")
    search_fields = ("title","description","slug","language__name","tags__name")
    autocomplete_fields = ("language","tags","created_by")
    readonly_fields = ("public_id","created_at","updated_at")
    inlines = [TestCaseInline]
    list_per_page = 30

@admin.register(Language)
class LanguageAdmin(ModelAdmin):
    list_display = ("name","code","is_active","supports_automatic_testing")
    list_filter = ("is_active","supports_automatic_testing")
    search_fields = ("name","code","slug")

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name","slug","created_at")
    search_fields = ("name","slug","description")

@admin.register(TestCase)
class TestCaseAdmin(ModelAdmin):
    list_display = ("question","order","is_active","is_hidden","comparison_mode","timeout")
    list_filter = ("is_active","is_hidden","comparison_mode")
    search_fields = ("question__title","name")

@admin.register(Submission)
class SubmissionAdmin(ModelAdmin):
    list_display = ("id","user","question","status","final_score","passed_tests_count","total_tests_count","created_at")
    list_filter = ("status","language","created_at")
    search_fields = ("user__email","user__username","question__title")
    readonly_fields = ("user","question","language","code","status","automatic_score","manual_score","final_score","passed_tests_count","failed_tests_count","total_tests_count","started_at","finished_at","execution_time","error_type","error_message","created_at","updated_at")
    list_per_page = 50

@admin.register(TestResult)
class TestResultAdmin(ModelAdmin):
    list_display = ("submission","test_order","status","passed","execution_time","created_at")
    list_filter = ("status","passed")
    search_fields = ("submission__question__title","error_type")
    readonly_fields = [f.name for f in TestResult._meta.fields]

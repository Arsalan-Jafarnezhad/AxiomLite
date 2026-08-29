from django.conf import settings
from django.db import models
from accounts.models.base import BaseModel
from questions.constants import EvaluationType, SubmissionStatus
from questions.managers.submission import SubmissionManager

class Submission(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="question_submissions")
    question = models.ForeignKey("questions.Question", on_delete=models.PROTECT, related_name="submissions")
    language = models.ForeignKey("questions.Language", on_delete=models.PROTECT, related_name="submissions")
    code = models.TextField()
    status = models.CharField(max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.PENDING, db_index=True)
    automatic_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    manual_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    final_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, db_index=True)
    passed_tests_count = models.PositiveIntegerField(default=0)
    failed_tests_count = models.PositiveIntegerField(default=0)
    total_tests_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    manual_feedback = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_question_submissions")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["user", "question", "-created_at"]),
            models.Index(fields=["question", "status"]),
            models.Index(fields=["question", "final_score"]),
            models.Index(fields=["user", "final_score"]),
        ]

    objects = SubmissionManager()

    def __str__(self):
        return f"#{self.pk} {self.question.title}"

    @property
    def is_solved(self):
        return self.final_score is not None and self.final_score == 100

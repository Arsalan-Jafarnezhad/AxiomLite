from django.db import models
from accounts.models.base import BaseModel
from questions.constants import TestResultStatus

class TestResult(BaseModel):
    submission = models.ForeignKey("questions.Submission", on_delete=models.CASCADE, related_name="test_results")
    test_case = models.ForeignKey("questions.TestCase", on_delete=models.PROTECT, related_name="results")
    test_order = models.PositiveIntegerField()
    status = models.CharField(max_length=32, choices=TestResultStatus.choices)
    passed = models.BooleanField(default=False)
    input_snapshot = models.JSONField(default=list)
    expected_output_snapshot = models.JSONField(default=list)
    actual_output = models.TextField(blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    execution_time = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    class Meta:
        ordering = ["test_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["submission", "test_order"], name="questions_result_submission_order"),
        ]
        indexes = [models.Index(fields=["submission", "test_order"])]

    def __str__(self):
        return f"Submission #{self.submission_id} · Test {self.test_order}"

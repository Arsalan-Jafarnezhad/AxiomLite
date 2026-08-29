from django.core.exceptions import ValidationError
from django.db import models
from accounts.models.base import BaseModel
from questions.constants import ComparisonMode

class TestCase(BaseModel):
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE, related_name="test_cases")
    order = models.PositiveIntegerField()
    name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    inputs = models.JSONField(default=list)
    expected_outputs = models.JSONField(default=list)
    is_active = models.BooleanField(default=True, db_index=True)
    timeout = models.DecimalField(max_digits=6, decimal_places=3, default=2)
    comparison_mode = models.CharField(max_length=32, choices=ComparisonMode.choices, default=ComparisonMode.EXACT)
    is_hidden = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["question", "order"], name="questions_testcase_question_order"),
        ]
        indexes = [models.Index(fields=["question", "is_active", "order"])]

    def clean(self):
        if not isinstance(self.inputs, list):
            raise ValidationError({"inputs": "Inputs must be a JSON list."})
        if not isinstance(self.expected_outputs, list):
            raise ValidationError({"expected_outputs": "Expected outputs must be a JSON list."})
        if self.timeout <= 0:
            raise ValidationError({"timeout": "Timeout must be greater than zero."})

    def __str__(self):
        return self.name or f"{self.question.title} · Test {self.order}"

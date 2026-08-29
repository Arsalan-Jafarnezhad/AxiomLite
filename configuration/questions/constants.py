from decimal import Decimal
from django.db import models

class Difficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"
    EXPERT = "expert", "Expert"

class QuestionStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"

class EvaluationType(models.TextChoices):
    AUTOMATIC = "automatic", "Automatic"
    MANUAL = "manual", "Manual"
    HYBRID = "hybrid", "Hybrid"

class SubmissionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    MANUAL_REVIEW = "manual_review", "Manual review"

class TestResultStatus(models.TextChoices):
    PASSED = "passed", "Passed"
    FAILED = "failed", "Failed"
    ERROR = "error", "Error"
    TIMEOUT = "timeout", "Timeout"
    SECURITY_ERROR = "security_error", "Security error"
    OUTPUT_LIMIT_EXCEEDED = "output_limit_exceeded", "Output limit exceeded"

class ComparisonMode(models.TextChoices):
    EXACT = "exact", "Exact"
    TRIMMED = "trimmed", "Trimmed"
    CASE_INSENSITIVE = "case_insensitive", "Case insensitive"
    WHITESPACE_INSENSITIVE = "whitespace_insensitive", "Whitespace insensitive"
    NUMERIC = "numeric", "Numeric"
    CUSTOM = "custom", "Custom"

ZERO = Decimal("0.00")
HUNDRED = Decimal("100.00")

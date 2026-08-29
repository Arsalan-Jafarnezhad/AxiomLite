from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from accounts.models.soft_delete import SoftDeleteModel
from questions.constants import Difficulty, QuestionStatus, EvaluationType
from questions.managers.question import QuestionManager

class Question(SoftDeleteModel):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, db_index=True)
    language = models.ForeignKey("questions.Language", on_delete=models.PROTECT, related_name="questions")
    tags = models.ManyToManyField("questions.Tag", blank=True, related_name="questions")
    status = models.CharField(max_length=12, choices=QuestionStatus.choices, default=QuestionStatus.DRAFT, db_index=True)
    evaluation_type = models.CharField(max_length=10, choices=EvaluationType.choices, default=EvaluationType.AUTOMATIC)
    evaluator = models.CharField(max_length=80, default="manual")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_questions")
    is_featured = models.BooleanField(default=False, db_index=True)
    sort_order = models.IntegerField(default=0, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    objects = QuestionManager()
    class Meta:
        permissions = [("publish_question", "Can publish question"), ("manage_test_cases", "Can manage test cases"), ("review_submission", "Can review submission")]
        ordering = ["sort_order", "-created_at", "id"]
        indexes = [
            models.Index(fields=["status", "difficulty"]),
            models.Index(fields=["status", "language"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["is_featured", "status"]),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.status == QuestionStatus.PUBLISHED and self.evaluation_type == EvaluationType.AUTOMATIC and self.pk:
            if not self.test_cases.filter(is_active=True).exists():
                raise ValidationError("Automatic questions require at least one active test before publication.")

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.title) or "question"
            slug, n = base, 1
            qs = type(self).all_objects.exclude(pk=self.pk)
            while qs.filter(slug=slug).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        if self.status == QuestionStatus.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == QuestionStatus.PUBLISHED and self.published_at and self.published_at <= timezone.now()

    def get_absolute_url(self):
        return reverse("questions:detail", kwargs={"slug": self.slug})

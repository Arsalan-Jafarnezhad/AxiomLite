from django.db import models
from questions.constants import QuestionStatus
from accounts.models.soft_delete import SoftDeleteQuerySet

class QuestionQuerySet(SoftDeleteQuerySet):
    def published(self):
        return self.filter(status=QuestionStatus.PUBLISHED, published_at__isnull=False)
    def drafts(self):
        return self.filter(status=QuestionStatus.DRAFT)
    def archived(self):
        return self.filter(status=QuestionStatus.ARCHIVED)
    def by_difficulty(self, value):
        return self.filter(difficulty=value) if value else self
    def by_language(self, language):
        return self.filter(language=language) if language else self
    def featured(self):
        return self.filter(is_featured=True)
    def search(self, query):
        if not query:
            return self
        return self.filter(
            models.Q(title__icontains=query)
            | models.Q(description__icontains=query)
            | models.Q(language__name__icontains=query)
            | models.Q(tags__name__icontains=query)
        ).distinct()

class QuestionManager(models.Manager.from_queryset(QuestionQuerySet)):
    pass

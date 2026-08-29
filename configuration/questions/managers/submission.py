from django.db import models
from questions.constants import SubmissionStatus

class SubmissionQuerySet(models.QuerySet):
    def completed(self): return self.filter(status=SubmissionStatus.COMPLETED)
    def pending(self): return self.filter(status=SubmissionStatus.PENDING)
    def running(self): return self.filter(status=SubmissionStatus.RUNNING)
    def manual_review(self): return self.filter(status=SubmissionStatus.MANUAL_REVIEW)
    def solved(self): return self.filter(final_score=100)

class SubmissionManager(models.Manager.from_queryset(SubmissionQuerySet)):
    pass

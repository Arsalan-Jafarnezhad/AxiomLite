from django.conf import settings
from django.db import transaction
from django.utils import timezone
from questions.constants import EvaluationType, SubmissionStatus
from questions.models import Submission

def create_submission(*, user, question, code):
    max_size = getattr(settings, "QUESTIONS_SUBMISSION_MAX_CODE_SIZE", 256 * 1024)
    if len(code.encode("utf-8")) > max_size:
        raise ValueError("Submission is too large.")
    with transaction.atomic():
        submission = Submission.objects.create(
            user=user,
            question=question,
            language=question.language,
            code=code,
            status=(
                SubmissionStatus.MANUAL_REVIEW
                if question.evaluation_type == EvaluationType.MANUAL
                else SubmissionStatus.PENDING
            ),
        )
    if question.evaluation_type != EvaluationType.MANUAL:
        from questions.tasks.submissions import evaluate_submission
        evaluate_submission.delay(submission.pk)
    return submission

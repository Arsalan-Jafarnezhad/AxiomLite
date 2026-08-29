from django.db import transaction
from django.utils import timezone
from questions.constants import SubmissionStatus
from questions.models import Submission
from questions.utils import clamp_score

@transaction.atomic
def review_submission(submission, *, reviewer, manual_score, feedback=""):
    if not reviewer.is_staff and not reviewer.has_perm("questions.review_submission"):
        raise PermissionError
    score=clamp_score(manual_score)
    submission.manual_score=score
    submission.manual_feedback=feedback
    submission.reviewed_by=reviewer
    submission.reviewed_at=timezone.now()
    submission.final_score=score
    submission.status=SubmissionStatus.COMPLETED
    submission.finished_at=submission.finished_at or timezone.now()
    submission.save(update_fields=["manual_score","manual_feedback","reviewed_by","reviewed_at","final_score","status","finished_at","updated_at"])
    return submission

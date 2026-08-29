from celery import shared_task

from questions.services.execution import evaluate_submission as run_evaluation


@shared_task(bind=True)
def evaluate_submission(self, submission_id):
    return run_evaluation(submission_id).pk

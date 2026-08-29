from django.conf import settings
from django.db import transaction
from django.utils import timezone
from questions.constants import EvaluationType, SubmissionStatus
from questions.execution.registry import get_executor
from questions.models import Submission, TestResult
from questions.services.scoring import automatic_score

def evaluate_submission(submission_id):
    submission = Submission.objects.select_related("question","language").get(pk=submission_id)
    if submission.status in {SubmissionStatus.COMPLETED, SubmissionStatus.FAILED}:
        return submission
    if submission.question.evaluation_type == EvaluationType.MANUAL:
        return submission
    tests = list(submission.question.test_cases.filter(is_active=True).order_by("order","id"))
    if not tests:
        return _fail(submission, "configuration_error", "No active tests are configured.")
    Submission.objects.filter(pk=submission.pk, status=SubmissionStatus.PENDING).update(
        status=SubmissionStatus.RUNNING, started_at=timezone.now()
    )
    submission.refresh_from_db()
    try:
        print("BEFORE EXECUTOR")

        executor = get_executor(submission.question.evaluator)
        
        print("EXECUTOR:", executor)
        
        report = executor.execute(submission, tests)
        
        print("AFTER EXECUTOR")
        with transaction.atomic():
            submission.test_results.all().delete()
            TestResult.objects.bulk_create([
                TestResult(
                    submission=submission, test_case_id=r.test_case_id, test_order=r.test_order,
                    status=r.status, passed=r.passed, input_snapshot=r.input_snapshot,
                    expected_output_snapshot=r.expected_output_snapshot, actual_output=r.actual_output,
                    error_type=r.error_type, error_message=r.error_message,
                    execution_time=r.execution_time,
                ) for r in report.tests
            ])
            submission.total_tests_count=report.total_tests
            submission.passed_tests_count=report.passed_tests
            submission.failed_tests_count=report.failed_tests
            submission.automatic_score=automatic_score(report.passed_tests, report.total_tests)
            submission.final_score=submission.automatic_score if submission.question.evaluation_type == EvaluationType.AUTOMATIC else None
            submission.status=SubmissionStatus.COMPLETED
            submission.finished_at=timezone.now()
            submission.execution_time=sum((r.execution_time or 0) for r in report.tests)
            submission.save(update_fields=[
                "total_tests_count","passed_tests_count","failed_tests_count","automatic_score",
                "final_score","status","finished_at","execution_time","updated_at"
            ])
        return submission
    # except Exception:
    #     return _fail(submission, "worker_failure", "The evaluator could not complete this submission.")
    except Exception as error:
        import logging
    
        logging.exception("Submission evaluation failed: %s", error)
        
        return _fail(
            submission,
            "worker_failure",
            str(error),
        )
def _fail(submission, error_type, message):
    Submission.objects.filter(pk=submission.pk).update(
        status=SubmissionStatus.FAILED,
        error_type=error_type,
        error_message=message,
        finished_at=timezone.now(),
    )
    return Submission.objects.get(pk=submission.pk)

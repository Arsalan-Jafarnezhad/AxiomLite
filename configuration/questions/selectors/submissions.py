from questions.models import Submission

def user_submissions(user):
    return (
        Submission.objects.filter(user=user)
        .select_related("question", "language")
        .prefetch_related("test_results")
    )

def submission_for_user(pk, user):
    return (
        user_submissions(user)
        .filter(pk=pk)
        .first()
    )

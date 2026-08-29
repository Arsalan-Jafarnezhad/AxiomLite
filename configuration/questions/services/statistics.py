from django.db.models import Avg, Count, Max, Min
from questions.constants import SubmissionStatus

def question_statistics(question):
    submissions = question.submissions.filter(status=SubmissionStatus.COMPLETED)
    attempting = submissions.values("user_id").distinct().count()
    solved = submissions.filter(final_score=100).values("user_id").distinct().count()
    rate = (solved / attempting * 100) if attempting else 0
    aggregates = submissions.aggregate(
        average_score=Avg("final_score"),
        best_score=Max("final_score"),
    )
    return {
        "attempting_users": attempting,
        "solved_users": solved,
        "solve_rate": round(rate, 2),
        "attempt_count": submissions.count(),
        **aggregates,
    }

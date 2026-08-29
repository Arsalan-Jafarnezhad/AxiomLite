from django.db.models import Avg, Count, Max, Min, Q
from questions.constants import SubmissionStatus

def get_question_statistics(question):
    qs = question.submissions.filter(status=SubmissionStatus.COMPLETED)
    attempting = qs.values("user_id").distinct().count()
    solved = qs.filter(final_score=100).values("user_id").distinct().count()
    return {
        "attempt_count": qs.count(),
        "attempting_users": attempting,
        "solved_users": solved,
        "solve_rate": round((solved / attempting * 100) if attempting else 0, 2),
        **qs.aggregate(average_score=Avg("final_score"), best_score=Max("final_score")),
    }

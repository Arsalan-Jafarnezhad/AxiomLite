from django.db.models import Count, Exists, OuterRef, Q

from questions.models import Question, Submission


def published_questions():
    return (
        Question.objects.published()
        .select_related("language", "created_by")
        .prefetch_related("tags")
    )


def question_for_user(slug, user=None):
    qs = published_questions().filter(slug=slug)

    if user and user.is_staff:
        qs = (
            Question.objects.filter(slug=slug)
            .select_related("language", "created_by")
            .prefetch_related("tags")
        )

    return qs.first()


def annotate_user_status(qs, user):
    if not user or not user.is_authenticated:
        return qs

    own = Submission.objects.filter(
        question=OuterRef("pk"),
        user=user,
    )

    solved = own.filter(
        final_score=100,
    )

    return qs.annotate(
        has_attempted=Exists(own),
        has_solved=Exists(solved),
    )


def annotate_question_statistics(qs):
    return qs.annotate(
        solve_count=Count(
            "submissions__user",
            filter=Q(
                submissions__final_score=100,
            ),
            distinct=True,
        ),
        try_count=Count(
            "submissions__user",
            distinct=True,
        ),
    )


def sort_questions(qs, sort="newest"):
    ordering = {
        "newest": "-created_at",
        "oldest": "created_at",
        "most_solved": "-solve_count",
        "least_solved": "solve_count",
        "most_attempted": "-try_count",
        "least_attempted": "try_count",
    }.get(sort, "-created_at")

    return qs.order_by(ordering)

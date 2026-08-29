from django.db.models import Prefetch, Count

from weblog.models import Comment


def article_comments(article):

    approved_replies = (
        Comment.objects.approved()
        .filter(
            parent__isnull=False,
        )
        .select_related(
            "author",
        )
        .order_by(
            "created_at",
        )
    )

    return (
        Comment.objects.approved()
        .root_comments()
        .filter(
            article=article,
        )
        .select_related(
            "author",
        )
        .prefetch_related(
            Prefetch(
                "replies",
                queryset=approved_replies,
            )
        )
        .recent()
    )


def pending_comments():

    return Comment.objects.pending().select_related(
        "author",
        "article",
    )


def user_comments(user):

    return (
        Comment.objects.filter(
            author=user,
        )
        .select_related(
            "article",
        )
        .order_by(
            "-created_at",
        )
    )


def comment_sentiments(article):

    return (
        Comment.objects.approved()
        .filter(
            article=article,
        )
        .values_list(
            "sentiment_score",
            flat=True,
        )
    )


def article_sentiment_summary(article):
    comments = (
        Comment.objects.approved()
        .filter(article=article)
        .values(
            "sentiment_label",
            "sentiment_score",
        )
    )

    summary = {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
    }

    scores = []

    for comment in comments:
        label = comment["sentiment_label"]

        if label in summary:
            summary[label] += 1

        scores.append(comment["sentiment_score"])

    total = sum(summary.values())

    # Aggregate sentiment:
    #
    #     sum(scores) / sum(abs(scores))
    #
    # This measures the balance of sentiment intensity rather
    # than simply averaging the individual scores.
    denominator = sum(abs(score) for score in scores)

    if denominator:
        sentiment_score = round(
            sum(scores) / denominator,
            4,
        )
    else:
        sentiment_score = 0.0

    if total:
        positive_percentage = round(
            summary["positive"] / total * 100,
            1,
        )

        negative_percentage = round(
            summary["negative"] / total * 100,
            1,
        )

        neutral_percentage = round(
            summary["neutral"] / total * 100,
            1,
        )
    else:
        positive_percentage = 0
        negative_percentage = 0
        neutral_percentage = 0

    return {
        **summary,
        "total": total,
        "positive_percentage": positive_percentage,
        "negative_percentage": negative_percentage,
        "neutral_percentage": neutral_percentage,
        # -1 → entirely negative
        #  0 → perfectly balanced
        # +1 → entirely positive
        "score": sentiment_score,
        # Convert [-1, +1] to [0, 100]
        "percentage": round(
            (sentiment_score + 1) * 50,
            1,
        ),
    }

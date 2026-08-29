"""
weblog/sentiment.py

Thin wrappers around VADER for comment sentiment analysis.

VADER returns a compound polarity score in the range [-1.0, 1.0].
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def polarity_score(text: str) -> float:
    """
    Return the compound VADER polarity score.

    Range:
        -1.0 = very negative
         0.0 = neutral
         1.0 = very positive
    """

    return _analyzer.polarity_scores(text)["compound"]


def is_positive(text: str) -> bool:
    return polarity_score(text) > 0


def is_negative(text: str) -> bool:
    return polarity_score(text) < 0


def is_neutral(text: str) -> bool:
    return polarity_score(text) == 0


def polarity_scores(texts: list[str]) -> list[float]:
    """
    Calculate polarity scores for multiple texts.
    """

    return [polarity_score(text) for text in texts]


def average_polarity(texts: list[str]) -> float:
    """
    Return the normalized aggregate sentiment score.

    Formula:
        sum(scores) / sum(abs(scores))

    Range:
        -1.0 = completely negative
         0.0 = balanced / neutral
         1.0 = completely positive

    Neutral-only input returns 0.
    """

    scores = polarity_scores(texts)

    denominator = sum(abs(score) for score in scores)

    if denominator == 0:
        return 0.0

    return round(
        sum(scores) / denominator,
        4,
    )


def sentiment_label(score: float) -> str:
    """
    Convert a VADER compound score into a human-readable label.
    """

    if score >= 0.05:
        return "positive"

    if score <= -0.05:
        return "negative"

    return "neutral"


def analyze(text: str) -> tuple[float, str]:
    """
    Analyze a single text and return:

        (score, label)
    """

    score = polarity_score(text)

    return (
        score,
        sentiment_label(score),
    )

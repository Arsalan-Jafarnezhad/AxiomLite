"""
shop/sentiment.py

Thin wrappers around VADER for sentiment analysis.
Importing this module requires ``vaderSentiment`` to be installed.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()  # Singleton — initialization is expensive


def polarity_score(text: str) -> float:
    """Returns the compound VADER polarity score in the range ``[-1.0, 1.0]``."""
    return _analyzer.polarity_scores(text)["compound"]


def is_positive(text: str) -> bool:
    return polarity_score(text) > 0


def is_negative(text: str) -> bool:
    return polarity_score(text) < 0


def is_neutral(text: str) -> bool:
    return polarity_score(text) == 0


def polarity_scores(texts: list[str]) -> list[float]:
    """Batch version of :func:`polarity_score`."""
    return [polarity_score(t) for t in texts]


def average_polarity(texts: list[str]) -> float:
    """
    Returns a 0–100 score representing *positive sentiment share*:

        positive_sum / (positive_sum + |negative_sum|) × 100

    Returns ``0`` when all texts are perfectly neutral.
    """
    scores = polarity_scores(texts)
    positive = sum(s for s in scores if s >= 0)
    negative = sum(abs(s) for s in scores if s < 0)
    total = positive + negative
    if total == 0:
        return 0.0
    return round(positive / total * 100, 2)

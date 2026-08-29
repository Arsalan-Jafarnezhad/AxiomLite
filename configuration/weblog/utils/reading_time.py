import re

from django.conf import settings
from django.utils.html import strip_tags


DEFAULT_WPM = getattr(
    settings,
    "WEBLOG_WORDS_PER_MINUTE",
    200,
)


_WORD_RE = re.compile(r"\w+")


def word_count(text: str) -> int:
    """
    Count human-readable words.
    """

    if not text:
        return 0

    text = strip_tags(text)

    return len(_WORD_RE.findall(text))


def reading_time(text: str, wpm: int = DEFAULT_WPM) -> int:
    """
    Calculate estimated reading time in minutes.
    """

    words = word_count(text)

    return max(
        1,
        (words + wpm - 1) // wpm,
    )
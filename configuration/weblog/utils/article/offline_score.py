# offline_score.py

from __future__ import annotations

from collections import Counter

from markdown_it import MarkdownIt

MIN_WORDS = 300
GOOD_WORDS = 800
IDEAL_WORDS = 1500

LONG_SENTENCE_WORDS = 30
VERY_LONG_SENTENCE_WORDS = 45
LONG_PARAGRAPH_WORDS = 120


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "her",
    "here",
    "hers",
    "him",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "may",
    "me",
    "more",
    "most",
    "much",
    "must",
    "my",
    "no",
    "not",
    "of",
    "on",
    "or",
    "our",
    "ours",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "to",
    "too",
    "under",
    "up",
    "us",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",
    "yours",
}


FILLER_PHRASES = (
    "in today's world",
    "it is important to note",
    "it is worth noting",
    "as we all know",
    "at the end of the day",
    "needless to say",
    "first and foremost",
    "in order to",
    "due to the fact that",
    "a wide range of",
    "as mentioned earlier",
    "as previously mentioned",
)


class ArticleOfflineAnalyzer:
    def __init__(self) -> None:
        self.md = MarkdownIt(
            "commonmark",
            {
                "html": True,
                "linkify": True,
                "typographer": True,
            },
        )

    def analyze(self, markdown: str) -> int:
        if not markdown or not markdown.strip():
            return 0

        tokens = self.md.parse(markdown)

        text = self._extract_text(tokens)
        words = self._words(text)
        sentences = self._sentences(text)
        paragraphs = self._paragraphs(tokens)

        if not words:
            return 0

        headings = self._headings(tokens)
        links = self._links(tokens)
        images = self._images(tokens)
        code_blocks = self._code_blocks(tokens)
        tables = self._tables(tokens)
        lists = self._lists(tokens)
        blockquotes = self._blockquotes(tokens)

        score = 0.0

        score += self._content_score(
            len(words),
            sentences,
            paragraphs,
        )

        score += self._structure_score(
            len(words),
            headings,
            paragraphs,
            lists,
            blockquotes,
        )

        score += self._readability_score(
            words,
            sentences,
            paragraphs,
        )

        score += self._writing_score(words)

        score += self._markdown_score(
            headings=headings,
            links=links,
            images=images,
            code_blocks=code_blocks,
            tables=tables,
            lists=lists,
            blockquotes=blockquotes,
        )

        score += self._reference_score(
            links,
            len(words),
        )

        return max(0, min(100, round(score)))

    @staticmethod
    def _extract_text(tokens) -> str:
        parts = []

        for token in tokens:
            if token.type == "inline":
                parts.append(token.content)
            elif token.type in {"fence", "code_block"}:
                parts.append(token.content)

        return "\n".join(parts)

    @staticmethod
    def _headings(tokens) -> list[dict]:
        headings = []

        for index, token in enumerate(tokens):
            if token.type != "heading_open":
                continue

            level = int(token.tag[1:])
            text = ""

            if index + 1 < len(tokens):
                next_token = tokens[index + 1]

                if next_token.type == "inline":
                    text = next_token.content.strip()

            headings.append(
                {
                    "level": level,
                    "text": text,
                }
            )

        return headings

    @staticmethod
    def _links(tokens) -> list[str]:
        links = []

        for token in tokens:
            if token.type != "inline" or not token.children:
                continue

            for child in token.children:
                if child.type != "link_open":
                    continue

                href = child.attrGet("href")

                if href:
                    links.append(href)

        return links

    @staticmethod
    def _images(tokens) -> list[str]:
        images = []

        for token in tokens:
            if token.type != "inline" or not token.children:
                continue

            for child in token.children:
                if child.type != "image":
                    continue

                src = child.attrGet("src")

                if src:
                    images.append(src)

        return images

    @staticmethod
    def _code_blocks(tokens) -> list[str]:
        return [
            token.content for token in tokens if token.type in {"fence", "code_block"}
        ]

    @staticmethod
    def _tables(tokens) -> int:
        return sum(token.type == "table_open" for token in tokens)

    @staticmethod
    def _lists(tokens) -> int:
        return sum(
            token.type
            in {
                "bullet_list_open",
                "ordered_list_open",
            }
            for token in tokens
        )

    @staticmethod
    def _blockquotes(tokens) -> int:
        return sum(token.type == "blockquote_open" for token in tokens)

    @staticmethod
    def _words(text: str) -> list[str]:
        words = []

        for word in text.lower().split():
            word = word.strip(".,!?;:()[]{}<>\"'`*_~")

            if word:
                words.append(word)

        return words

    @staticmethod
    def _sentences(text: str) -> list[str]:
        sentences = []
        current = []

        for word in text.replace("\n", " ").split():
            current.append(word)

            if word.endswith((".", "!", "?")):
                sentence = " ".join(current).strip()

                if sentence:
                    sentences.append(sentence)

                current = []

        if current:
            sentence = " ".join(current).strip()

            if sentence:
                sentences.append(sentence)

        return sentences

    @staticmethod
    def _paragraphs(tokens) -> list[str]:
        paragraphs = []

        for index, token in enumerate(tokens):
            if token.type != "paragraph_open":
                continue

            if index + 1 >= len(tokens):
                continue

            inline = tokens[index + 1]

            if inline.type != "inline":
                continue

            text = inline.content.strip()

            if text:
                paragraphs.append(text)

        return paragraphs

    @staticmethod
    def _content_score(
        word_count: int,
        sentences: list[str],
        paragraphs: list[str],
    ) -> float:
        score = 0.0

        if word_count >= MIN_WORDS:
            score += 8
        elif word_count >= 200:
            score += 5
        elif word_count >= 100:
            score += 2

        if word_count >= GOOD_WORDS:
            score += 4

        if word_count >= IDEAL_WORDS:
            score += 2

        if len(sentences) >= 10:
            score += 2

        if len(paragraphs) >= 5:
            score += 2

        return min(score, 18)

    @classmethod
    def _structure_score(
        cls,
        word_count: int,
        headings: list[dict],
        paragraphs: list[str],
        lists: int,
        blockquotes: int,
    ) -> float:
        score = 0.0

        if headings:
            score += 6

        if len(headings) >= 2:
            score += 4

        if len(headings) >= 4:
            score += 2

        if cls._valid_heading_hierarchy(headings):
            score += 3

        if word_count >= 500 and len(headings) >= 2:
            score += 2

        if paragraphs:
            score += 2

        if lists:
            score += 2

        if blockquotes:
            score += 1

        return min(score, 22)

    @staticmethod
    def _valid_heading_hierarchy(
        headings: list[dict],
    ) -> bool:
        if not headings:
            return False

        previous = headings[0]["level"]

        for heading in headings[1:]:
            current = heading["level"]

            if current > previous + 1:
                return False

            previous = current

        return True

    def _readability_score(
        self,
        words: list[str],
        sentences: list[str],
        paragraphs: list[str],
    ) -> float:
        if not words or not sentences:
            return 0.0

        long_sentences = sum(
            len(self._words(sentence)) >= LONG_SENTENCE_WORDS for sentence in sentences
        )

        very_long_sentences = sum(
            len(self._words(sentence)) >= VERY_LONG_SENTENCE_WORDS
            for sentence in sentences
        )

        average_sentence_length = len(words) / len(sentences)

        score = 20.0

        if average_sentence_length > 20:
            score -= 3

        if average_sentence_length > 25:
            score -= 3

        if average_sentence_length > 30:
            score -= 4

        score -= min(
            5,
            long_sentences / len(sentences) * 10,
        )

        score -= min(
            5,
            very_long_sentences / len(sentences) * 15,
        )

        long_paragraphs = sum(
            len(self._words(paragraph)) >= LONG_PARAGRAPH_WORDS
            for paragraph in paragraphs
        )

        score -= min(
            4,
            long_paragraphs * 1.5,
        )

        return max(0, min(20, score))

    @staticmethod
    def _writing_score(words: list[str]) -> float:
        if not words:
            return 0.0

        meaningful = [
            word for word in words if word not in STOPWORDS and len(word) >= 3
        ]

        if not meaningful:
            return 5.0

        score = 20.0

        unique_ratio = len(set(meaningful)) / len(meaningful)

        if unique_ratio < 0.25:
            score -= 8
        elif unique_ratio < 0.35:
            score -= 5
        elif unique_ratio < 0.45:
            score -= 2

        counts = Counter(meaningful)

        repeated_words = sum(max(0, count - 8) for count in counts.values())

        score -= min(
            6,
            repeated_words / 5,
        )

        filler_count = sum(
            ArticleOfflineAnalyzer._count_phrase(
                words,
                phrase,
            )
            for phrase in FILLER_PHRASES
        )

        score -= min(
            6,
            filler_count * 1.5,
        )

        return max(0, min(20, score))

    @staticmethod
    def _count_phrase(
        words: list[str],
        phrase: str,
    ) -> int:
        phrase_words = phrase.lower().split()

        if not phrase_words:
            return 0

        count = 0
        size = len(phrase_words)

        for index in range(len(words) - size + 1):
            if words[index : index + size] == phrase_words:
                count += 1

        return count

    @staticmethod
    def _markdown_score(
        *,
        headings: list[dict],
        links: list[str],
        images: list[str],
        code_blocks: list[str],
        tables: int,
        lists: int,
        blockquotes: int,
    ) -> float:
        score = 0.0

        if headings:
            score += 3

        if lists:
            score += 2

        if blockquotes:
            score += 1

        if images:
            score += 2

        if tables:
            score += 2

        if code_blocks:
            score += 3

        if links:
            score += 2

        return min(score, 15)

    @staticmethod
    def _reference_score(
        links: list[str],
        word_count: int,
    ) -> float:
        if not links:
            return 0.0

        ratio = len(links) / max(word_count, 1) * 1000

        if ratio >= 3:
            return 5.0

        if ratio >= 2:
            return 4.0

        if ratio >= 1:
            return 3.0

        return 2.0


def analyze_article_score(markdown: str) -> int:
    return ArticleOfflineAnalyzer().analyze(markdown)

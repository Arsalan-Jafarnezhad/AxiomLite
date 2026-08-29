# weblog/utils/article/analyzer.py

from __future__ import annotations

from dataclasses import asdict

from django.conf import settings

from weblog.utils.article.ai_score import LLMArticleAnalyzer
from weblog.utils.article.markdown import MarkdownAnalysis
from weblog.utils.article.offline_score import analyze_article_score


class ArticleAnalyzer:
    def __init__(self) -> None:
        self.markdown = MarkdownAnalysis()
        self.llm = LLMArticleAnalyzer(
            model=getattr(
                settings,
                "LM_STUDIO_MODEL",
                "empero-ai/qwen3.8-2b-distill",
            ),
            timeout=getattr(
                settings,
                "LM_STUDIO_TIMEOUT",
                30,
            ),
        )

    def analyze(
        self,
        markdown: str,
    ) -> tuple[int, int, dict | None]:
        offline_score = analyze_article_score(markdown)
        images = self.markdown.images(markdown)

        try:
            result = self.llm.analyze(
                markdown,
                images,
            )

        except Exception as e:
            print(e)
            return offline_score, None, None
        return offline_score, result.score, asdict(result)

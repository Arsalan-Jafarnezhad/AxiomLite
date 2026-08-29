# weblog/utils/article/ai_score.py

from __future__ import annotations

import json
from dataclasses import dataclass

from openai import OpenAI


@dataclass(slots=True)
class LLMArticleAnalysis:
    score: int
    content_quality: int
    structure_quality: int
    readability: int
    writing_quality: int
    markdown_quality: int
    image_quality: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    image_analysis: list[str]


class LLMArticleAnalyzer:
    BASE_URL = "http://localhost:1234/v1"
    API_KEY = "lm-studio"

    def __init__(
        self,
        model: str,
        timeout: float = 30.0,
    ) -> None:
        self.model = model
        self.client = OpenAI(
            base_url=self.BASE_URL,
            api_key=self.API_KEY,
            timeout=timeout,
        )

    def analyze(
        self,
        markdown: str,
        images: list[dict] | None = None,
    ) -> LLMArticleAnalysis:
        images = images or []

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self._system_prompt(),
                },
                {
                    "role": "user",
                    "content": self._build_user_prompt(
                        markdown,
                        images,
                    ),
                },
            ],
            response_format=self._response_format(),
            temperature=0.1,
            max_tokens=1000,
            stream=False,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("LM Studio returned an empty response.")

        return self._parse_result(json.loads(content))

    @staticmethod
    def _system_prompt() -> str:
        return """
You are an expert article quality evaluator.

Evaluate the provided Markdown article objectively.

The score must represent ARTICLE QUALITY, not popularity,
author reputation, number of views, or engagement.

Evaluate:

- usefulness and completeness
- clarity
- organization
- readability
- writing quality
- originality
- repetition
- filler
- headings and structure
- examples
- links and references
- Markdown structure
- code blocks when relevant
- tables and lists when useful
- images and alt text

Do not reward Markdown features merely because they exist.

Return only the requested JSON structure.
""".strip()

    @staticmethod
    def _build_user_prompt(
        markdown: str,
        images: list[dict],
    ) -> str:
        image_information = "\n".join(
            f"- URL: {image.get('src', '')}\n" f"  Alt: {image.get('alt', '')}"
            for image in images
        )

        if not image_information:
            image_information = "No Markdown images were detected."

        return f"""
Analyze this article.

## ARTICLE MARKDOWN

{markdown}

## DETECTED MARKDOWN IMAGES

{image_information}

Important:

- Score from 0 to 100.
- Do not invent information about images.
- Evaluate only information reasonably available.
- Keep suggestions concise and actionable.
""".strip()

    @staticmethod
    def _response_format() -> dict:
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "article_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "content_quality": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "structure_quality": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "readability": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "writing_quality": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "markdown_quality": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "image_quality": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "strengths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 8,
                        },
                        "weaknesses": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 8,
                        },
                        "suggestions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 8,
                        },
                        "image_analysis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 8,
                        },
                    },
                    "required": [
                        "score",
                        "content_quality",
                        "structure_quality",
                        "readability",
                        "writing_quality",
                        "markdown_quality",
                        "image_quality",
                        "strengths",
                        "weaknesses",
                        "suggestions",
                        "image_analysis",
                    ],
                    "additionalProperties": False,
                },
            },
        }

    @staticmethod
    def _parse_result(data: dict) -> LLMArticleAnalysis:
        score = data["score"]

        if not isinstance(score, int):
            raise ValueError("LLM score must be an integer.")

        if not 0 <= score <= 100:
            raise ValueError("LLM score must be between 0 and 100.")

        return LLMArticleAnalysis(
            score=score,
            content_quality=data["content_quality"],
            structure_quality=data["structure_quality"],
            readability=data["readability"],
            writing_quality=data["writing_quality"],
            markdown_quality=data["markdown_quality"],
            image_quality=data["image_quality"],
            strengths=data["strengths"],
            weaknesses=data["weaknesses"],
            suggestions=data["suggestions"],
            image_analysis=data["image_analysis"],
        )

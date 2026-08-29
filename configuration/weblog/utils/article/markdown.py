# markdown.py

from __future__ import annotations

from markdown_it import MarkdownIt


class MarkdownAnalysis:
    def __init__(self) -> None:
        self.md = MarkdownIt(
            "commonmark",
            {
                "html": True,
                "linkify": True,
                "typographer": True,
            },
        )

    def images(self, markdown: str) -> list[dict]:
        if not markdown:
            return []

        tokens = self.md.parse(markdown)
        images = []

        for token in tokens:
            if token.type != "inline" or not token.children:
                continue

            for child in token.children:
                if child.type != "image":
                    continue

                src = child.attrGet("src")

                if not src:
                    continue

                images.append(
                    {
                        "src": src,
                        "alt": child.content or "",
                        "title": child.attrGet("title") or "",
                    }
                )

        return images
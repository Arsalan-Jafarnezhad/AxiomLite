# import markdown


# def render_markdown(text: str) -> str:

#     return markdown.markdown(
#         text,
#         extensions=[
#             "extra",
#             "tables",
#             "toc",
#             "fenced_code",
#         ],
#     )
from markdown_it import MarkdownIt


markdown = (
    MarkdownIt(
        "commonmark",
        {
            "html": True,
            "breaks": True,
            "linkify": True,
            "typographer": True,
        },
    )
    .enable(
        [
            "table",
            "strikethrough",
            "autolink",
        ]
    )
)


def render_markdown(content):
    """
    Render article Markdown as HTML.

    Supports:

    - headings
    - paragraphs
    - bold
    - italic
    - strikethrough
    - inline code
    - fenced code blocks
    - ordered lists
    - unordered lists
    - nested lists
    - links
    - images
    - tables
    - blockquotes
    - horizontal rules
    - line breaks
    - automatic links
    - raw HTML
    """

    if not content:
        return ""

    return markdown.render(
        str(content)
    )
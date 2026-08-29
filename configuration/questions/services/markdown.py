from django.conf import settings
from weblog.utils.markdown import render_markdown

def render_question_markdown(source):
    html = render_markdown(source)
    if not getattr(settings, "QUESTIONS_SANITIZE_MARKDOWN", False):
        return html
    try:
        import bleach
    except ImportError:
        raise RuntimeError("QUESTIONS_SANITIZE_MARKDOWN requires bleach.")
    return bleach.clean(
        html,
        tags=[
            "a","abbr","b","blockquote","br","code","del","em","h1","h2","h3","h4","h5","h6",
            "hr","i","img","li","ol","p","pre","strong","table","tbody","td","th","thead","tr","ul",
        ],
        attributes={"a": ["href","title","target","rel"], "img": ["src","alt","title","width","height"]},
        protocols=["http","https","mailto"],
    )

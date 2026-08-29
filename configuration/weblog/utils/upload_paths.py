from pathlib import Path


def article_cover_path(
    instance,
    filename,
):

    extension = Path(filename).suffix

    return (
        f"weblog/articles/"
        f"{instance.author_id}/"
        f"{instance.slug}/"
        f"cover{extension}"
    )


def article_media_path(
    instance,
    filename,
):

    extension = Path(filename).suffix

    return (
        f"weblog/articles/"
        f"{instance.article.author_id}/"
        f"{instance.article.slug}/"
        f"{filename}"
    )

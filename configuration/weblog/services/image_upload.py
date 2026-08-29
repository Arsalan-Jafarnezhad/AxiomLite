from pathlib import Path
from uuid import uuid4

from django.core.files.storage import default_storage


def save_article_image(uploaded_file):

    extension = Path(
        uploaded_file.name
    ).suffix.lower()

    filename = (
        f"weblog/articles/"
        f"{uuid4().hex}{extension}"
    )

    path = default_storage.save(
        filename,
        uploaded_file,
    )

    return default_storage.url(path)
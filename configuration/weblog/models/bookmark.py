from django.conf import settings
from django.db import models


class Bookmark(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks"
    )

    article = models.ForeignKey(
        "weblog.Article", on_delete=models.CASCADE, related_name="bookmarks"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "article"]

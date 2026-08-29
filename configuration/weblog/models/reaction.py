from django.conf import settings
from django.db import models


class Reaction(models.Model):

    article = models.ForeignKey(
        "weblog.Article", on_delete=models.CASCADE, related_name="reactions"
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    emoji = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["article", "user", "emoji"]

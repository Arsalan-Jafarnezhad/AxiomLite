from django.conf import settings
from django.db import models


class ArticleView(models.Model):

    article = models.ForeignKey(
        "weblog.Article", on_delete=models.CASCADE, related_name="views"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

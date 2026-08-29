from django.db import models


class Media(models.Model):

    article = models.ForeignKey(
        "weblog.Article", on_delete=models.CASCADE, related_name="media"
    )

    file = models.FileField(upload_to="weblog/media/")

    caption = models.CharField(max_length=200, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

from django.db import models


class ArticleSEO(models.Model):

    article = models.OneToOneField(
        "weblog.Article", on_delete=models.CASCADE, related_name="seo"
    )

    meta_title = models.CharField(max_length=200, blank=True)

    meta_description = models.TextField(blank=True)

    canonical_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Article SEO"

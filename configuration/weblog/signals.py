from django.db.models.signals import post_save

from django.dispatch import receiver

from weblog.models import (
    Article,
    ArticleSEO,
)


@receiver(
    post_save,
    sender=Article,
)
def create_article_seo(
    sender,
    instance,
    created,
    **kwargs,
):

    if created:

        ArticleSEO.objects.get_or_create(
            article=instance,
        )

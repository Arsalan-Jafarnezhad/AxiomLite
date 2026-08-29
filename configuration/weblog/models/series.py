from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from weblog.utils.slug import unique_slug


class Series(models.Model):
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Series")
        verbose_name_plural = _("Series")
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Series, self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("weblog:series", kwargs={"slug": self.slug})

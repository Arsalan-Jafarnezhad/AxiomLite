from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from weblog.utils.slug import unique_slug


class Tag(models.Model):
    name = models.CharField(_("Name"), max_length=50, unique=True)
    slug = models.SlugField(_("Slug"), max_length=60, unique=True, blank=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Tag, self.name, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("weblog:tag", kwargs={"slug": self.slug})

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from weblog.utils.slug import unique_slug


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=120, unique=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, self.name, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("weblog:category", kwargs={"slug": self.slug})

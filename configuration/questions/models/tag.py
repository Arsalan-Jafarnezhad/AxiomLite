from django.db import models
from django.utils.text import slugify
from accounts.models.base import BaseModel

class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "tag"
            slug = base
            n = 1
            qs = type(self).objects.exclude(pk=self.pk)
            while qs.filter(slug=slug).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

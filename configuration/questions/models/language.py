from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models.base import BaseModel

class Language(BaseModel):
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=120, unique=True)
    code = models.CharField(_("Code"), max_length=50, unique=True)
    is_active = models.BooleanField(default=True, db_index=True)
    supports_automatic_testing = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["is_active", "name"])]

    def __str__(self):
        return self.name

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from .base import BaseModel


class Address(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    title = models.CharField(_("Label"), max_length=100, help_text=_("e.g. Home, Office."))
    receiver_name = models.CharField(_("Receiver name"), max_length=100)
    phone_number = PhoneNumberField(_("Phone number"))
    country = CountryField(_("Country"))
    province = models.CharField(_("Province/State"), max_length=64)
    city = models.CharField(_("City"), max_length=64)
    postal_code = models.CharField(_("Postal code"), max_length=20)
    address = models.TextField(_("Street address"))
    is_default = models.BooleanField(_("Default address"), default=False)

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ["-is_default", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} — {self.receiver_name}"

    def save(self, *args, **kwargs) -> None:
        # Only one default address per user — demoting the others is cheaper
        # than adding a partial-unique constraint per backend, and this is a
        # low-write model.
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

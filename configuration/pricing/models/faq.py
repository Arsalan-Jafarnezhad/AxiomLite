"""
pricing/models/faq.py

Standalone FAQ entries shown on the pricing page (not tied to a single Plan).
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import ActiveQuerySet, OrderedModel


class PricingFAQ(OrderedModel):
    question = models.CharField(_("Question"), max_length=300)
    answer = models.TextField(_("Answer"))
    active = models.BooleanField(_("Active"), default=True, db_index=True)

    objects = ActiveQuerySet.as_manager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("Pricing FAQ")
        verbose_name_plural = _("Pricing FAQs")

    def __str__(self) -> str:
        return self.question

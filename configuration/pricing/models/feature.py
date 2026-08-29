"""
pricing/models/feature.py

A single feature row shown under a Plan (e.g. "Unlimited revisions").
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import OrderedModel
from .plan import Plan


class PlanFeature(OrderedModel):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="features", verbose_name=_("Plan"))

    title = models.CharField(_("Title"), max_length=200)
    description = models.CharField(_("Description"), max_length=300, blank=True)

    included = models.BooleanField(_("Included"), default=True)
    highlight = models.BooleanField(_("Highlight"), default=False, help_text=_("Highlight this feature in UI."))
    icon = models.CharField(_("Icon"), max_length=50, default="check_circle")

    class Meta(OrderedModel.Meta):
        verbose_name = _("Plan Feature")
        verbose_name_plural = _("Plan Features")

    def __str__(self) -> str:
        return self.title

    @property
    def display_icon(self) -> str:
        """Falls back to a sensible default icon based on inclusion status."""
        if self.icon:
            return self.icon
        return "check_circle" if self.included else "cancel"

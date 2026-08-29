"""
pricing/models/attribute.py

Free-form key/value spec rows attached to a Plan (e.g. "Storage" -> "50GB"),
with a `typed_value` accessor that casts `value` according to `value_type`
instead of every caller having to parse the raw string themselves.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import OrderedModel
from .plan import Plan

TRUE_STRINGS = {"1", "true", "yes", "on"}


class PlanAttribute(OrderedModel):
    class ValueType(models.TextChoices):
        TEXT = "text", _("Text")
        NUMBER = "number", _("Number")
        BOOLEAN = "boolean", _("Boolean")

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="attributes", verbose_name=_("Plan"))

    name = models.CharField(_("Name"), max_length=100)
    value = models.CharField(_("Value"), max_length=200)
    value_type = models.CharField(
        _("Value type"), max_length=20, choices=ValueType.choices, default=ValueType.TEXT
    )
    icon = models.CharField(_("Icon"), max_length=50, blank=True)

    class Meta(OrderedModel.Meta):
        verbose_name = _("Plan Attribute")
        verbose_name_plural = _("Plan Attributes")
        constraints = [
            models.UniqueConstraint(fields=["plan", "name"], name="unique_plan_attribute_name"),
        ]

    def __str__(self) -> str:
        return f"{self.plan} - {self.name}"

    @property
    def typed_value(self) -> str | float | bool:
        """``value`` cast to a real Python type according to ``value_type``."""
        if self.value_type == self.ValueType.NUMBER:
            try:
                return float(self.value)
            except ValueError:
                return 0.0
        if self.value_type == self.ValueType.BOOLEAN:
            return self.value.strip().lower() in TRUE_STRINGS
        return self.value

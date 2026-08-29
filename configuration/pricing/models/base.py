"""
pricing/models/base.py

Small shared building blocks so the concrete models below stay declarative
instead of repeating the same "active/featured" filtering logic everywhere.
"""

from __future__ import annotations

from django.db import models


class ActiveQuerySet(models.QuerySet):
    """Common filters shared by every model that has an ``active`` flag."""

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(active=True, featured=True)


class OrderedModel(models.Model):
    """
    Abstract base for anything that's manually ordered via a small
    ``order`` integer and displayed in that order by default.
    """

    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ("order", "id")

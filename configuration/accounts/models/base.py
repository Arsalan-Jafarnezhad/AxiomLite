"""Base models shared by the accounts application."""

from django.db import models

from accounts.utils.ids import generate_public_id


class BaseModel(models.Model):
    """Abstract base model providing public identity and timestamps."""

    public_id = models.CharField(
        max_length=32,
        unique=True,
        default=generate_public_id,
        editable=False,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from accounts.utils.upload_paths import rank_image_upload_path
from .base import BaseModel


class Rank(BaseModel):
    name = models.CharField(
        max_length=64,
        unique=True,
        validators=[MinLengthValidator(2)],
    )
    description = models.TextField(max_length=2048, blank=True)
    activation_level = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    priority = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to=rank_image_upload_path, blank=True)

    class Meta:
        ordering = ["-priority"]
        constraints = [
            models.UniqueConstraint(fields=["priority"], name="unique_rank_priority")
        ]

    def __str__(self):
        return self.name

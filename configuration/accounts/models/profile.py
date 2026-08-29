from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from math import sqrt

from accounts.utils.upload_paths import profile_image_upload_path

from .soft_delete import SoftDeleteModel

AVATAR_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


class Profile(SoftDeleteModel):
    """
    Public profile information (avatar, bio, gamification).

    Authentication and security data belongs on ``User``; anything meant
    to be shown on a public profile page belongs here instead.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User"),
    )
    avatar = models.ImageField(
        _("Avatar"),
        upload_to=profile_image_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=AVATAR_EXTENSIONS)],
    )
    display_name = models.CharField(_("Display name"), max_length=150, blank=True)
    biography = models.TextField(_("Biography"), blank=True)
    points = models.PositiveIntegerField(_("Points"), default=0, db_index=True)
    level = models.PositiveIntegerField(_("Level"), default=0, db_index=True)
    is_private = models.BooleanField(
        _("Private profile"),
        default=False,
        help_text=_("When enabled, only a minimal profile page is shown to other visitors."),
    )

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self.display_name or self.user.full_name or self.user.email

    @property
    def avatar_url(self) -> str:
        return self.avatar.url if self.avatar else ""
    def update_level(self) -> None:
        self.level = max(
            0,
            int(
                (-95 + sqrt(95 * 95 + 20 * self.points)) // 10
            ),
        )
    
    
    def add_points(self, amount: int) -> None:
        if amount <= 0:
            return
    
        self.points += amount
        self.update_level()
    
        self.save(
            update_fields=["points", "level"],
        )
    
    
    def remove_points(self, amount: int) -> None:
        if amount <= 0:
            return
    
        self.points = max(
            self.points - amount,
            0,
        )
    
        self.update_level()
    
        self.save(
            update_fields=["points", "level"],
        )
        


    @property
    def current_points(self):
        level = self.level
        total_points_for_level = 5 * level * level + 95 * level
        return self.points - total_points_for_level


    @property
    def needed_points(self):
        return 100 + self.level * 10
    
    @property
    def level_points(self):
        return self.current_points + self.needed_points

    @property
    def progress_percent(self):
        return round(self.current_points / self.level_points * 100, 2)
    
    @property
    def completion_percent(self) -> int:
        score = 0
        total = 103

        user = self.user

        if self.avatar:
            score += 15

        if self.display_name:
            score += 10

        if self.biography:
            score += 15

        if user.first_name:
            score += 8

        if user.last_name:
            score += 8

        if user.username:
            score += 8

        if user.phone_number:
            score += 8

        if user.is_phone_number_verified:
            score += 6

        if user.born_date:
            score += 6

        if user.gender:
            score += 4

        if user.is_email_verified:
            score += 12

        if user.preferred_language:
            score += 3

        return round(score / total * 100)
    
    @property
    def missing_profile_items(self) -> list[str]:
        missing = []
        user = self.user

        if not self.avatar:
            missing.append("Avatar")

        if not self.display_name:
            missing.append("Display Name")

        if not self.biography:
            missing.append("Biography")

        if not user.first_name:
            missing.append("First Name")

        if not user.last_name:
            missing.append("Last Name")

        if not user.phone_number:
            missing.append("Phone Number")

        if not user.is_phone_number_verified:
            missing.append("Phone Verification")

        if not user.born_date:
            missing.append("Birth Date")

        if not user.gender:
            missing.append("Gender")

        if not user.is_email_verified:
            missing.append("Email Verification")
        return missing
"""Custom user model for the accounts application."""

from datetime import date

import phonenumbers
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from accounts.managers import AllUserManager, UserManager

from .soft_delete import SoftDeleteModel

OFFICIAL_GROUPS = [
    "Founder",
    "Owner",
    "Manager",
]


class User(AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
    """Email-first custom user model."""

    class Gender(models.IntegerChoices):
        MALE = 1, _("Male")
        FEMALE = 2, _("Female")

    username = models.CharField(
        _("Username"),
        max_length=50,
        unique=True,
        blank=True,
        db_index=True,
        help_text=_(
            "Public handle. Auto-generated from your email if left blank.",
        ),
    )
    email = models.EmailField(
        _("Email address"),
        unique=True,
        db_index=True,
    )
    phone_number = PhoneNumberField(
        _("Phone number"),
        unique=True,
        blank=True,
        null=True,
    )

    first_name = models.CharField(
        _("First name"),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _("Last name"),
        max_length=150,
        blank=True,
    )
    born_date = models.DateField(
        _("Birth date"),
        blank=True,
        null=True,
        help_text=_("Format: YYYY-MM-DD"),
    )
    gender = models.PositiveSmallIntegerField(
        _("Gender"),
        choices=Gender.choices,
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(
        _("Verified"),
        default=False,
    )
    is_staff = models.BooleanField(
        _("Staff status"),
        default=False,
        help_text=_("Can access Django administration."),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
    )

    accepts_sms = models.BooleanField(
        _("Accept SMS notifications"),
        default=True,
    )
    accepts_marketing_emails = models.BooleanField(
        _("Accept marketing emails"),
        default=True,
    )
    preferred_language = models.CharField(
        _("Preferred language"),
        max_length=10,
        default="en",
    )

    date_joined = models.DateTimeField(
        _("Date joined"),
        auto_now_add=True,
    )
    email_verified_at = models.DateTimeField(
        _("Email verified at"),
        blank=True,
        null=True,
    )
    phone_number_verified_at = models.DateTimeField(
        _("Phone verified at"),
        blank=True,
        null=True,
    )
    last_login_ip = models.GenericIPAddressField(
        _("Last login IP"),
        blank=True,
        null=True,
        protocol="both",
    )
    last_login_country = CountryField(
        _("Last login country"),
        blank=True,
        null=True,
    )
    last_activity_at = models.DateTimeField(
        _("Last activity"),
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()
    all_objects = AllUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]
        constraints = [
            UniqueConstraint(
                Lower("username"),
                name="unique_username_ci",
            ),
        ]

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs) -> None:
        """Generate a username when one was not explicitly provided."""
        if not self.username:
            self.username = self._generate_unique_username()

        super().save(*args, **kwargs)

    def _generate_unique_username(self) -> str:
        """Generate an available username from the email local part."""
        base = (
            slugify(
                self.email.split("@", 1)[0],
            )
            or "user"
        )

        username = base
        suffix = 1

        while (
            User.all_objects.filter(username__iexact=username)
            .exclude(pk=self.pk)
            .exists()
        ):
            suffix += 1
            username = f"{base}{suffix}"

        return username

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def short_name(self) -> str:
        """Return the most useful short display name."""
        return self.first_name or self.username or self.email

    @property
    def age(self) -> int | None:
        """Return the user's current age."""
        if not self.born_date:
            return None

        today = date.today()
        had_birthday = (
            today.month,
            today.day,
        ) >= (
            self.born_date.month,
            self.born_date.day,
        )

        return today.year - self.born_date.year - (0 if had_birthday else 1)

    @property
    def is_email_verified(self) -> bool:
        """Return whether the email has been verified."""
        return self.email_verified_at is not None

    @property
    def is_phone_number_verified(self) -> bool:
        """Return whether the phone number has been verified."""
        return self.phone_number_verified_at is not None

    @property
    def is_official(self) -> bool:
        """Return whether the user belongs to an official group."""
        return self.groups.filter(
            name__in=OFFICIAL_GROUPS,
        ).exists()

    def verify_email(self) -> None:
        """Mark the user's email as verified."""
        self.email_verified_at = timezone.now()
        self.is_verified = True
        self.save(
            update_fields=[
                "email_verified_at",
                "is_verified",
            ],
        )

    def verify_phone_number(self) -> None:
        """Mark the user's phone number as verified."""
        self.phone_number_verified_at = timezone.now()
        self.save(
            update_fields=[
                "phone_number_verified_at",
            ],
        )

    def update_last_activity(self) -> None:
        """Update the user's last activity timestamp."""
        self.last_activity_at = timezone.now()
        self.save(
            update_fields=[
                "last_activity_at",
            ],
        )

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True
        self.save(update_fields=["is_active"])

    def get_full_name(self) -> str:
        """Return the user's full name for Django compatibility."""
        return self.full_name

    def get_short_name(self) -> str:
        """Return the user's short name for Django compatibility."""
        return self.short_name

    def get_phone_number_country_short_name(self) -> str | None:
        """Return the ISO country code associated with the phone number."""
        if not self.phone_number:
            return None

        try:
            parsed = phonenumbers.parse(
                str(self.phone_number),
                None,
            )
            region = phonenumbers.geocoder.region_code_for_number(parsed)
        except phonenumbers.NumberParseException:
            return None

        return region.lower() if region else None

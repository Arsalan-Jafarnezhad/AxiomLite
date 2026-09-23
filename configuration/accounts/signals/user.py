"""Signal receivers for the accounts app."""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Every user gets a Profile the moment their account is created."""
    if created:
        Profile.objects.get_or_create(user=instance)

# """Signals related to the User model."""

# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from accounts.models import User


# @receiver(post_save, sender=User)
# def create_user_profile(
#     sender,
#     instance: User,
#     created: bool,
#     **kwargs,
# ) -> None:
#     """Create a profile automatically when a user is created."""
#     if not created:
#         return

#     instance.profile
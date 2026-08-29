from django.db import models


class UserQuerySet(models.QuerySet):

    def verified(self):
        return self.filter(is_verified=True)

    def staff(self):
        return self.filter(is_staff=True)

    def by_username(self, username):
        return self.filter(username__iexact=username)

    def get_by_username(self, username):
        """Case-insensitive lookup returning ``None`` instead of raising."""
        return self.by_username(username).first()

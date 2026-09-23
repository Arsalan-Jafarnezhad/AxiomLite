"""Profile serializers."""

from rest_framework import serializers

from accounts.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize the authenticated user's profile."""

    avatar_url = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    completion_percent = serializers.IntegerField(read_only=True)
    current_points = serializers.IntegerField(read_only=True)
    needed_points = serializers.IntegerField(read_only=True)
    level_points = serializers.IntegerField(read_only=True)
    progress_percent = serializers.FloatField(read_only=True)
    missing_profile_items = serializers.ListField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "public_id",
            "display_name",
            "biography",
            "avatar",
            "avatar_url",
            "points",
            "level",
            "is_private",
            "name",
            "completion_percent",
            "current_points",
            "needed_points",
            "level_points",
            "progress_percent",
            "missing_profile_items",
        ]
        read_only_fields = [
            "public_id",
            "avatar_url",
            "points",
            "level",
            "name",
            "completion_percent",
            "current_points",
            "needed_points",
            "level_points",
            "progress_percent",
            "missing_profile_items",
        ]


class PublicProfileSerializer(serializers.ModelSerializer):
    """Serialize information intended for public profiles."""

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    name = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "public_id",
            "username",
            "name",
            "avatar_url",
            "biography",
            "points",
            "level",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        """Hide private profile information from other users."""
        data = super().to_representation(instance)

        request = self.context.get("request")
        request_user = getattr(request, "user", None)

        if instance.is_private and request_user != instance.user:
            data.pop("biography", None)
            data.pop("points", None)
            data.pop("level", None)

        return data

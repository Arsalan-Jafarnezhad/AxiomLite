"""Account serializers."""

from rest_framework import serializers

from accounts.models import User


class AccountSerializer(serializers.ModelSerializer):
    """Serialize the authenticated user's account information."""

    full_name = serializers.CharField(
        read_only=True,
    )
    short_name = serializers.CharField(
        read_only=True,
    )
    is_email_verified = serializers.BooleanField(
        read_only=True,
    )
    is_phone_number_verified = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = User

        fields = [
            "public_id",
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "born_date",
            "gender",
            "preferred_language",
            "accepts_sms",
            "accepts_marketing_emails",
            "full_name",
            "short_name",
            "is_verified",
            "is_email_verified",
            "is_phone_number_verified",
            "date_joined",
            "last_activity_at",
        ]

        read_only_fields = [
            "public_id",
            "email",
            "full_name",
            "short_name",
            "is_verified",
            "is_email_verified",
            "is_phone_number_verified",
            "date_joined",
            "last_activity_at",
        ]
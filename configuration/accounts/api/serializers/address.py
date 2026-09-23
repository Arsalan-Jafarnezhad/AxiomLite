"""Address serializers."""

from rest_framework import serializers

from accounts.models import Address


class AddressSerializer(serializers.ModelSerializer):
    """Serialize an address belonging to the authenticated user."""

    public_id = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Address

        fields = [
            "public_id",
            "title",
            "receiver_name",
            "phone_number",
            "country",
            "province",
            "city",
            "postal_code",
            "address",
            "is_default",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "public_id",
            "created_at",
            "updated_at",
        ]
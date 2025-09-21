from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PMSUser
User = get_user_model()


class OAuthLoginSerializer(serializers.Serializer):
    """Serializer for OAuth login requests."""
    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.strip().lower()

    def validate_name(self, value):
        """Clean and validate name field."""
        return value.strip() if value else ""


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with limited fields."""
    name = serializers.SerializerMethodField()

    class Meta:
        model = PMSUser
        fields = ['email', 'full_name', 'sub_id']

    def get_name(self, obj):
        """Get full name from first and last name."""
        name_parts = [obj.first_name, obj.last_name]
        return ' '.join(part for part in name_parts if part).strip()


class OAuthLoginResponseSerializer(serializers.Serializer):
    """Serializer for OAuth login response."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    created = serializers.BooleanField()
    user = UserSerializer()

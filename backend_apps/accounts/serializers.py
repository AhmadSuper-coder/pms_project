from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PMSUser
User = get_user_model()


class OAuthLoginSerializer(serializers.Serializer):
    """Serializer for OAuth login requests."""
    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=255, required=True, allow_blank=True)
    sub  = serializers.CharField(max_length=255, required=True, allow_blank=True)
    profile_picture = serializers.URLField(max_length=500, required=False, allow_blank=True)

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.strip().lower()

    def validate_name(self, value):
        """Clean and validate name field."""
        return value.strip() if value else ""
    
    def validate_sub(self, value):
        """Clean and validate sub field."""
        return value.strip() if value else ""
    
    def validate_profile_picture(self, value):
        """Clean and validate profile picture URL."""
        return value.strip() if value else ""


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with limited fields."""

    class Meta:
        model = PMSUser
        fields = ['email', 'full_name', 'sub_id']



class OAuthLoginResponseSerializer(serializers.Serializer):
    """Serializer for OAuth login response."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    created = serializers.BooleanField()
    user = UserSerializer()

import re
from typing import Any, Dict

from rest_framework import serializers


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[+]?\d{8,15}$")


class GenerateOtpSerializer(serializers.Serializer):
    channel = serializers.ChoiceField(choices=["sms", "whatsapp", "email"], required=True)
    identifier = serializers.CharField(required=True, max_length=255)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        channel = attrs.get("channel")
        identifier = (attrs.get("identifier") or "").strip()
        if channel == "email":
            if not EMAIL_REGEX.match(identifier):
                raise serializers.ValidationError({"identifier": "Invalid email format"})
        else:
            if not PHONE_REGEX.match(identifier):
                raise serializers.ValidationError({"identifier": "Invalid phone format (use E.164)"})
        attrs["identifier"] = identifier
        return attrs


class VerifyOtpSerializer(GenerateOtpSerializer):
    code = serializers.RegexField(regex=r"^\d{4,8}$", required=True, max_length=8)



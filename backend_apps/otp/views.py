import re
from typing import Any, Dict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import create_and_store_otp, validate_otp
from .providers import dispatch_otp, OtpDeliveryError


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[+]?\d{8,15}$")


def _parse_json(request) -> Dict[str, Any]:
    try:
        import json

        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


def _validate_channel(channel: str) -> bool:
    return channel in {"sms", "whatsapp", "email"}


def _validate_identifier(channel: str, identifier: str) -> bool:
    if channel == "email":
        return bool(EMAIL_REGEX.match(identifier))
    return bool(PHONE_REGEX.match(identifier))


@csrf_exempt
@require_POST
def generate_otp_view(request):
    payload = _parse_json(request)
    channel = str(payload.get("channel", "")).lower()
    identifier = str(payload.get("identifier", "")).strip()

    if not _validate_channel(channel):
        return JsonResponse({"detail": "Invalid channel"}, status=400)

    if not _validate_identifier(channel, identifier):
        return JsonResponse({"detail": "Invalid identifier"}, status=400)

    try:
        code, expires_at = create_and_store_otp(identifier)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=429)

    try:
        dispatch_otp(channel, identifier, code)
    except OtpDeliveryError as e:
        return JsonResponse({"detail": str(e)}, status=500)

    return JsonResponse({"detail": "OTP sent", "expires_at": expires_at})


@csrf_exempt
@require_POST
def verify_otp_view(request):
    payload = _parse_json(request)
    channel = str(payload.get("channel", "")).lower()
    identifier = str(payload.get("identifier", "")).strip()
    code = str(payload.get("code", "")).strip()

    if not _validate_channel(channel):
        return JsonResponse({"detail": "Invalid channel"}, status=400)

    if not _validate_identifier(channel, identifier):
        return JsonResponse({"detail": "Invalid identifier"}, status=400)

    if not code or not code.isdigit():
        return JsonResponse({"detail": "Invalid code"}, status=400)

    ok = validate_otp(identifier, code)
    if not ok:
        return JsonResponse({"detail": "Invalid or expired code"}, status=400)

    return JsonResponse({"detail": "Verified"})



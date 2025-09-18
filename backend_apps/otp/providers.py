from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail


class OtpDeliveryError(Exception):
    pass


@dataclass
class OtpMessage:
    identifier: str
    channel: str
    code: str


def send_via_email(identifier: str, code: str) -> None:
    subject = getattr(settings, "OTP_EMAIL_SUBJECT", "Your verification code")
    message = getattr(settings, "OTP_EMAIL_TEMPLATE", "Your OTP code is: {code}").format(code=code)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if not from_email:
        raise OtpDeliveryError("DEFAULT_FROM_EMAIL is not configured")
    send_mail(subject, message, from_email, [identifier], fail_silently=False)


def send_via_sms(identifier: str, code: str) -> None:
    # Placeholder for real SMS provider (e.g., Twilio). In production, implement here.
    # Fail if provider is marked as required without credentials.
    require_config = getattr(settings, "OTP_REQUIRE_PROVIDER_CONFIG", False)
    if require_config:
        account = getattr(settings, "SMS_TWILIO_ACCOUNT_SID", None)
        token = getattr(settings, "SMS_TWILIO_AUTH_TOKEN", None)
        sender = getattr(settings, "SMS_TWILIO_SENDER", None)
        if not (account and token and sender):
            raise OtpDeliveryError("SMS provider not configured")
    # For now, no-op. Integrate SDK here if desired.
    return None


def send_via_whatsapp(identifier: str, code: str) -> None:
    # Placeholder for WhatsApp provider via Twilio/Meta Graph. Same guard as SMS.
    require_config = getattr(settings, "OTP_REQUIRE_PROVIDER_CONFIG", False)
    if require_config:
        account = getattr(settings, "WA_TWILIO_ACCOUNT_SID", None)
        token = getattr(settings, "WA_TWILIO_AUTH_TOKEN", None)
        sender = getattr(settings, "WA_TWILIO_SENDER", None)
        if not (account and token and sender):
            raise OtpDeliveryError("WhatsApp provider not configured")
    return None


def dispatch_otp(channel: str, identifier: str, code: str) -> None:
    channel = channel.lower()
    if channel == "email":
        send_via_email(identifier, code)
    elif channel == "sms":
        send_via_sms(identifier, code)
    elif channel == "whatsapp":
        send_via_whatsapp(identifier, code)
    else:
        raise OtpDeliveryError("Unsupported channel")



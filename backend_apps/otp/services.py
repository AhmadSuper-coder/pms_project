import random
import time
from dataclasses import dataclass
from typing import Optional, Tuple

from django.conf import settings
from django.core.cache import cache


OTP_CODE_LENGTH = getattr(settings, "OTP_CODE_LENGTH", 6)
OTP_TTL_SECONDS = getattr(settings, "OTP_TTL_SECONDS", 300)
OTP_MAX_ATTEMPTS = getattr(settings, "OTP_MAX_ATTEMPTS", 5)
OTP_RESEND_COOLDOWN_SECONDS = getattr(settings, "OTP_RESEND_COOLDOWN_SECONDS", 30)


def _otp_key(identifier: str) -> str:
    return f"otp:code:{identifier}"


def _otp_attempts_key(identifier: str) -> str:
    return f"otp:attempts:{identifier}"


def _otp_send_window_key(identifier: str) -> str:
    return f"otp:send_cooldown:{identifier}"


def generate_numeric_code(length: int) -> str:
    lower = 10 ** (length - 1)
    upper = (10 ** length) - 1
    return str(random.randint(lower, upper))


@dataclass
class OtpPayload:
    identifier: str
    channel: str  # "sms" | "whatsapp" | "email"
    code: str
    expires_at_epoch: int


def create_and_store_otp(identifier: str) -> Tuple[str, int]:
    existing_cooldown = cache.get(_otp_send_window_key(identifier))
    if existing_cooldown:
        raise ValueError("OTP recently sent. Please wait before requesting another.")

    code = generate_numeric_code(OTP_CODE_LENGTH)
    expires_at = int(time.time()) + OTP_TTL_SECONDS
    cache.set(_otp_key(identifier), code, timeout=OTP_TTL_SECONDS)
    cache.set(_otp_attempts_key(identifier), 0, timeout=OTP_TTL_SECONDS)
    cache.set(_otp_send_window_key(identifier), True, timeout=OTP_RESEND_COOLDOWN_SECONDS)
    return code, expires_at


def validate_otp(identifier: str, submitted_code: str) -> bool:
    stored_code: Optional[str] = cache.get(_otp_key(identifier))
    if stored_code is None:
        return False

    attempts_key = _otp_attempts_key(identifier)
    attempts = cache.get(attempts_key) or 0
    if attempts >= OTP_MAX_ATTEMPTS:
        cache.delete(_otp_key(identifier))
        cache.delete(attempts_key)
        return False

    if submitted_code == stored_code:
        cache.delete(_otp_key(identifier))
        cache.delete(attempts_key)
        return True

    # increment attempts
    attempts += 1
    remaining = max(1, int(cache.ttl(_otp_key(identifier)) or OTP_TTL_SECONDS))
    cache.set(attempts_key, attempts, timeout=remaining)
    return False



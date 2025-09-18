OTP Service (Email, SMS, WhatsApp)

Endpoints

- POST /api/otp/generate
  - body: { "channel": "email|sms|whatsapp", "identifier": "email or E.164 phone" }
  - 200: { "detail": "OTP sent", "expires_at": 1730000000 }
  - 400/429/500 with { "detail": "..." }

- POST /api/otp/verify
  - body: { "channel": "email|sms|whatsapp", "identifier": "email or phone", "code": "123456" }
  - 200: { "detail": "Verified" }
  - 400: { "detail": "Invalid or expired code" }

Behavior

- Codes are numeric with configurable length (default 6), expire after OTP_TTL_SECONDS (default 300s), and are single-use.
- Attempts are throttled (OTP_MAX_ATTEMPTS default 5) and resend has cooldown (OTP_RESEND_COOLDOWN_SECONDS default 30s).
- Storage uses Django cache; configure Redis in production.

Settings (env)

- OTP_CODE_LENGTH (default 6)
- OTP_TTL_SECONDS (default 300)
- OTP_MAX_ATTEMPTS (default 5)
- OTP_RESEND_COOLDOWN_SECONDS (default 30)
- OTP_EMAIL_SUBJECT (default "Your verification code")
- OTP_EMAIL_TEMPLATE (default "Your OTP code is: {code}")
- OTP_REQUIRE_PROVIDER_CONFIG (default false)
- DEFAULT_FROM_EMAIL (required in production)
- EMAIL_* (standard Django email settings)
- SMS_TWILIO_ACCOUNT_SID, SMS_TWILIO_AUTH_TOKEN, SMS_TWILIO_SENDER (if enforcing SMS config)
- WA_TWILIO_ACCOUNT_SID, WA_TWILIO_AUTH_TOKEN, WA_TWILIO_SENDER (if enforcing WhatsApp config)

Production Cache (Redis example)

In `pms_backend/settings.py` add:

```
CACHES = {
  'default': {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': 'redis://localhost:6379/1',
    'OPTIONS': {
      'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    }
  }
}
```

Security Notes

- Always use HTTPS.
- Keep resend cooldown and attempt limits to mitigate brute-force.
- Use strong email backend and vetted SMS/WhatsApp provider; current SMS/WhatsApp functions are placeholders to be integrated with your provider.

Frontend Usage

- Start verification: POST /api/otp/generate
- Confirm: POST /api/otp/verify
- After success, proceed to your next step (e.g., create a session or mark contact verified).



from django.apps import AppConfig


class OtpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend_apps.otp"
    label = "otp"
    verbose_name = "OTP Service"



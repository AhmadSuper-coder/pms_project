from django.urls import path
from .views import generate_otp_view, verify_otp_view


urlpatterns = [
    path("generate", generate_otp_view, name="otp-generate"),
    path("verify", verify_otp_view, name="otp-verify"),
]



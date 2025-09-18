from django.urls import path
from .views import GenerateOtpView, VerifyOtpView


urlpatterns = [
    path("generate", GenerateOtpView.as_view(), name="otp-generate"),
    path("verify", VerifyOtpView.as_view(), name="otp-verify"),
]



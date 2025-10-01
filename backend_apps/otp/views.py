from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .services import create_and_store_otp, validate_otp
from .providers import dispatch_otp, OtpDeliveryError
from .serializers import GenerateOtpSerializer, VerifyOtpSerializer


class GenerateOtpView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GenerateOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = serializer.validated_data["channel"].lower()
        identifier = serializer.validated_data["identifier"]
        try:
            code, expires_at = create_and_store_otp(identifier)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            dispatch_otp(channel, identifier, code)
        except OtpDeliveryError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "success": True,
            "message": "OTP sent successfully",
            "expires_at": expires_at,
            "data": {
                "identifier": identifier,
                "channel": channel
            }
        },
        status=status.HTTP_200_OK)


class VerifyOtpView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = serializer.validated_data["channel"].lower()
        identifier = serializer.validated_data["identifier"]
        code = serializer.validated_data["code"]

        ok = validate_otp(identifier, code)
        if not ok:
            return Response({"detail": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Verified"}, status=status.HTTP_200_OK)



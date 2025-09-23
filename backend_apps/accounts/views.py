from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PMSUser
from .serializers import OAuthLoginSerializer, OAuthLoginResponseSerializer, UserSerializer


class OAuthLoginView(APIView):
    """
    OAuth login endpoint for external authentication providers.
    
    Expected input from Next.js after provider auth:
    { "email": "...", "name": "Optional" }
    """
    permission_classes = [AllowAny]
    serializer_class = OAuthLoginSerializer

    def post(self, request):
        """Handle OAuth login request."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        name = serializer.validated_data.get('name', '')

        with transaction.atomic():
            user, created = PMSUser.objects.get_or_create(
                email=email,
                full_name=name,
            )

        refresh = RefreshToken.for_user(user)
                    
        user_serializer = UserSerializer(user)
        
        response_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "created": created,
            "user": user_serializer.data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



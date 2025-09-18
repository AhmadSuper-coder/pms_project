from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def oauth_login(request):
    # Expected input from Next.js after provider auth:
    # { "email": "...", "name": "Optional" }
    email = (request.data.get("email") or "").strip().lower()
    name = (request.data.get("name") or "").strip()
    if not email:
        return Response({"detail": "email required"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0], "first_name": name.split(" ")[0] if name else "", "last_name": " ".join(name.split(" ")[1:]) if name and len(name.split()) > 1 else ""},
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "created": created,
            "user": {"id": user.id, "email": user.email, "name": f"{user.first_name} {user.last_name}".strip()},
        }
    )



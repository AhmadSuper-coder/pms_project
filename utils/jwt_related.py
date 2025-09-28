import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from backend_apps.accounts.models import PMSUser


def get_user_id_from_jwt(request):
    """Extract user_id from JWT token in the request headers."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthenticationFailed('Authorization header missing or invalid')

    token = auth_header.split(' ')[1]

    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )

        user_id = decoded_token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('user_id not found in token')

        return int(user_id)

    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
    except (ValueError, TypeError):
        raise AuthenticationFailed('Invalid user_id in token')
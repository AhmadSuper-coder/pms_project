from django.urls import path
from .views import oauth_login


urlpatterns = [
    path('oauth-login', oauth_login, name='oauth-login'),
]



from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OAuthLoginView

router = DefaultRouter()
# Add any ViewSets here if we create them later

urlpatterns = [
    path('oauth-login/', OAuthLoginView.as_view(), name='oauth-login'),
] + router.urls



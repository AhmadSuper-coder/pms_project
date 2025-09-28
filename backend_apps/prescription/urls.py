from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, MedicineViewSet

router = DefaultRouter()
router.register(r'', PrescriptionViewSet, basename='prescription')
router.register(r'medicines', MedicineViewSet, basename='medicine')

urlpatterns = router.urls
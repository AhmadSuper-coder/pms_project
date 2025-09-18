from django.urls import path
from .views import PatientCRUDView

urlpatterns = [
    path('patients', PatientCRUDView.as_view(), name='patient-list-create'),
    path('patients/<int:patient_id>', PatientCRUDView.as_view(), name='patient-detail'),
]


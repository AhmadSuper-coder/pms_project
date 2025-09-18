from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GcsSignUploadUrlView, ConfirmUploadView, PatientDocumentsView, DocumentDetailView, DocumentViewSet


router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path("sign-upload", GcsSignUploadUrlView.as_view(), name="doc-sign-upload"),
    path("confirm", ConfirmUploadView.as_view(), name="doc-confirm"),
    path("patient/<int:patient_id>/documents", PatientDocumentsView.as_view(), name="patient-documents"),
    path("documents/<int:document_id>", DocumentDetailView.as_view(), name="document-detail"),
    path('', include(router.urls)),
]



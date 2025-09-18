from django.urls import path
from .views import (
    GcsSignUploadUrlView,
    ConfirmUploadView,
    PatientDocumentsView,
    DocumentDetailView,
    DocumentCRUDView,
)


urlpatterns = [
    path("sign-upload", GcsSignUploadUrlView.as_view(), name="doc-sign-upload"),
    path("confirm", ConfirmUploadView.as_view(), name="doc-confirm"),
    path("patient/<int:patient_id>/documents", PatientDocumentsView.as_view(), name="patient-documents"),
    path("documents/<int:document_id>", DocumentDetailView.as_view(), name="document-detail"),
    path("documents", DocumentCRUDView.as_view(), name="document-list-create"),
    path("documents/<int:document_id>", DocumentCRUDView.as_view(), name="document-update-delete"),
]



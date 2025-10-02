from typing import Any

from django.db import models
from backend_apps.patient.models import Patient
from backend_apps.accounts.models import PMSUser
from non_django.error_handling.exceptions import GlobalException




class Document(models.Model):
    owner = models.ForeignKey(
        PMSUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="documents",
        help_text="The staff member (e.g., doctor, admin) who uploaded or owns this document."
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="documents",
        help_text="The patient this document is associated with. Deleting the patient will also delete this document."
    )
    filename = models.CharField(
        max_length=255,
        help_text="Original filename of the uploaded file (e.g., blood_test_report.pdf)."
    )
    content_type = models.CharField(
        max_length=150,
        help_text="MIME type of the document (e.g., application/pdf, image/jpeg)."
    )
    gcs_key = models.CharField(
        max_length=512,
        unique=True,
        help_text="Unique key or path used to store and retrieve the file from Google Cloud Storage."
    )
    document_type = models.CharField(
        max_length=100,
        help_text="Category or type of the document (e.g., Lab Report, Prescription, Scan)."
    )
    size_bytes = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes (useful for validating upload limits)."
    )
    is_uploaded = models.BooleanField(
        default=False,
        help_text="Indicates whether the document has been successfully uploaded to storage."
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Description of the document."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the document record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="The date and time when the document record was last updated."
    )


    def __str__(self):
        return f"{self.filename} ({self.patient.full_name})"


    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.filename} ({self.gcs_key})"


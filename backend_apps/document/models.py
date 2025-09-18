from django.db import models
from django.contrib.auth import get_user_model
from backend_apps.patient.models import Patient


User = get_user_model()


class Document(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="documents")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="documents")
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=150)
    gcs_key = models.CharField(max_length=512, unique=True)
    document_type = models.CharField(max_length=100)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    is_uploaded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.filename} ({self.gcs_key})"



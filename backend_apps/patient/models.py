from django.db import models
from backend_apps.accounts.models import PMSUser




class Patient(models.Model):
    doctor = models.ForeignKey(PMSUser, on_delete=models.CASCADE, related_name="patients")
    mobile_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    known_allergies = models.TextField(null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)
    lifestyle_information = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.mobile_number})"

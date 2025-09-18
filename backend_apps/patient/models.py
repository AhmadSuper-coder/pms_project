from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Patient(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")
    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.mobile_number})"

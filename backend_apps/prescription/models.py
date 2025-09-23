from django.db import models
from backend_apps.patient.models import Patient
from backend_apps.accounts.models import PMSUser
# Create your models here.

class Prescription(models.Model):
    doctor = models.ForeignKey(PMSUser, on_delete=models.CASCADE, related_name="prescriptions", null=True, blank=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="prescriptions",
        help_text="The patient for whom this prescription is created."
    )
    special_instructions = models.TextField(
        null=True,
        blank=True,
        help_text="Any special instructions for the patient."
    )
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional follow-up date for the patient."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription for {self.patient.full_name} ({self.created_at.date()})"


class Medicine(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="medicines",
        help_text="The patient this medicine is prescribed to.",
        null=True,
        blank=True
    )
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="medicines",
        help_text="The prescription this medicine belongs to."
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the medicine (e.g., Arnica 30C)."
    )
    dosage = models.CharField(
        max_length=100,
        help_text="Dosage instructions (e.g., 5 drops)."
    )
    frequency = models.CharField(
        max_length=100,
        help_text="How often the medicine should be taken (e.g., 3 times a day)."
    )
    duration = models.CharField(
        max_length=100,
        help_text="How long the medicine should be taken (e.g., 15 days)."
    )

    def __str__(self):
        return f"{self.name} ({self.dosage})"

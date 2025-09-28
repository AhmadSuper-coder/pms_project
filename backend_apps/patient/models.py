from django.db import models
from backend_apps.accounts.models import PMSUser



class Patient(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        DISCHARGED = "discharged", "Discharged"
        TRANSFERRED = "transferred", "Transferred"
        DECEASED = "deceased", "Deceased"

    doctor = models.ForeignKey(PMSUser, on_delete=models.CASCADE, related_name="patients")
    mobile_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GenderChoices.choices,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Current status of the patient"
    )
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=255, null=True, blank=True)
    known_allergies = models.TextField(null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)
    lifestyle_information = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["doctor", "status"]),
            models.Index(fields=["mobile_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.mobile_number}) - {self.get_status_display()}"

    @property
    def is_active(self):
        """Check if patient is active"""
        return self.status == self.StatusChoices.ACTIVE

    def activate(self):
        """Activate the patient"""
        self.status = self.StatusChoices.ACTIVE
        self.save(update_fields=['status', 'updated_at'])

    def deactivate(self):
        """Deactivate the patient"""
        self.status = self.StatusChoices.INACTIVE
        self.save(update_fields=['status', 'updated_at'])
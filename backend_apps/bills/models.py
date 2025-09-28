from django.db import models
from backend_apps.accounts.models import PMSUser
from backend_apps.patient.models import Patient

# Create your models here.

class Bill(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        UPI = "upi", "UPI"
        CARD = "card", "Card"
        ONLINE_TRANSFER = "online_transfer", "Online Transfer"
        OTHER = "other", "Other"

    doctor = models.ForeignKey(
        PMSUser,
        on_delete=models.CASCADE,
        related_name="bills",
        help_text="Doctor who issued the bill",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="bills",
        help_text="Patient for whom the bill is generated",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["doctor", "patient"]),
            models.Index(fields=["status"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"Bill #{self.id} - {self.patient.full_name} - {self.amount} ({self.status})"
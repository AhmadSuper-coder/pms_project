from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "mobile_number", "age", "gender", "doctor", "created_at")
    list_filter = ("gender", "doctor", "created_at")
    search_fields = ("full_name", "mobile_number", "email", "address")
    ordering = ("full_name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic Information", {
            "fields": ("full_name", "mobile_number", "email", "doctor")
        }),
        ("Personal Details", {
            "fields": ("age", "gender", "date_of_birth", "address", "emergency_contact")
        }),
        ("Medical Information", {
            "fields": ("known_allergies", "medical_history", "lifestyle_information")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
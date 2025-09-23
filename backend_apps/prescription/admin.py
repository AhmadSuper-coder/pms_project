from django.contrib import admin
from .models import Prescription, Medicine

# Register your models here.


class MedicineInline(admin.TabularInline):
    model = Medicine
    extra = 1  # show 1 empty row by default
    fields = ("name", "dosage", "frequency", "duration")
    verbose_name = "Medicine"
    verbose_name_plural = "Medicines"


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("patient", "follow_up_date", "created_at")
    list_filter = ("follow_up_date", "created_at")
    search_fields = ("patient__full_name", "patient__mobile_number")
    date_hierarchy = "created_at"
    inlines = [MedicineInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Prescription Details", {
            "fields": ("patient", "special_instructions", "follow_up_date")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "dosage", "frequency", "duration", "prescription")
    list_filter = ("prescription",)
    search_fields = ("name", "prescription__patient__full_name")

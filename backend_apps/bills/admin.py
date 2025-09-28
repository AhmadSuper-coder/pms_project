from django.contrib import admin
from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "amount", "date", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "doctor", "date", "created_at")
    search_fields = ("patient__full_name", "patient__mobile_number", "doctor__full_name", "doctor__email")
    date_hierarchy = "date"
    ordering = ("-date", "-created_at")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Bill Information", {
            "fields": ("doctor", "patient", "amount", "date")
        }),
        ("Payment Details", {
            "fields": ("status", "payment_method", "notes")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def get_queryset(self, request):
        # Optimize queries by selecting related objects
        return super().get_queryset(request).select_related("doctor", "patient")

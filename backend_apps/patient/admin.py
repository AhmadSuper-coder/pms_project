
# backend_apps/patient/admin.py
from django.contrib import admin
from .models import Patient

# @admin.register(Patient)
# class PatientAdmin(admin.ModelAdmin):
#     list_display = ('full_name', 'mobile_number', 'doctor', 'date_of_birth', 'gender', 'created_at')
#     search_fields = ('full_name', 'mobile_number', 'doctor__email', 'doctor__full_name')
#     list_filter = ('gender', 'doctor')
#     ordering = ('full_name',)

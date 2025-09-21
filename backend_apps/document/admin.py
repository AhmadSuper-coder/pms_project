# backend_apps/patient/admin.py
from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'patient', 'owner', 'document_type', 'is_uploaded', 'size_bytes', 'created_at')
    search_fields = ('filename', 'gcs_key', 'patient__full_name', 'owner__email')
    list_filter = ('document_type', 'is_uploaded', 'created_at')
    ordering = ('-created_at',)

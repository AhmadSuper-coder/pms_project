# backend_apps/patient/admin.py
from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'patient','description', 'owner', 'is_uploaded', 'document_type','size_bytes', 'created_at')
    search_fields = ('filename', 'gcs_key', 'patient__full_name', 'owner__email')
    list_filter = ('document_type', 'is_uploaded','description', 'created_at')
    ordering = ('-created_at',)

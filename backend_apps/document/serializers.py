from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'owner', 'patient', 'filename', 'content_type', 'gcs_key', 'document_type', 'size_bytes', 'is_uploaded', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'gcs_key', 'is_uploaded', 'created_at', 'updated_at']



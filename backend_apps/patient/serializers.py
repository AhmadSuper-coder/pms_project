from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'doctor', 'full_name', 'mobile_number', 'date_of_birth', 'gender', 'allergies', 'medical_history', 'created_at', 'updated_at']
        read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']



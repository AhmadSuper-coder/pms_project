from rest_framework import serializers
from .models import Patient
from backend_apps.prescription.models import Prescription

# class PatientSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Patient
#         fields = ['id', 'doctor', 'full_name', 'mobile_number', 'date_of_birth', 'gender', 'allergies', 'medical_history', 'created_at', 'updated_at']
#         read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']



class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']  # Make doctor read-only

# class AppointmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Appointment
#         fields = "__all__"





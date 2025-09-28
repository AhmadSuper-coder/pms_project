from rest_framework import serializers
from .models import Bill
from backend_apps.patient.models import Patient


class BillSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_mobile = serializers.CharField(source='patient.mobile_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Bill
        exclude = ['doctor']  # Exclude doctor from response (auto-set from JWT)
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'amount': {'required': False},  # Make optional for updates
            'date': {'required': False},
            'status': {'required': False},
            'payment_method': {'required': False},
            'patient': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional for updates
        if self.context.get('request') and self.context['request'].method in ['PUT', 'PATCH']:
            for field_name, field in self.fields.items():
                if field_name not in ['id', 'created_at', 'updated_at']:
                    field.required = False
from rest_framework import serializers
from .models import Prescription, Medicine
from backend_apps.patient.models import Patient


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'dosage', 'frequency', 'duration']


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_mobile = serializers.CharField(source='patient.mobile_number', read_only=True)
    medicines = MedicineSerializer(many=True, read_only=True)
    medicines_count = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        exclude = ['doctor']  # Exclude doctor from response (auto-set from JWT)
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'patient': {'required': False},  # Make optional for updates
            'special_instructions': {'required': False},
            'follow_up_date': {'required': False},
        }

    def get_medicines_count(self, obj):
        return obj.medicines.count()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional for updates
        if self.context.get('request') and self.context['request'].method in ['PUT', 'PATCH']:
            for field_name, field in self.fields.items():
                if field_name not in ['id', 'created_at', 'updated_at']:
                    field.required = False


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True, required=False)

    class Meta:
        model = Prescription
        exclude = ['doctor']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        prescription = Prescription.objects.create(**validated_data)

        # Create medicines
        for medicine_data in medicines_data:
            Medicine.objects.create(
                prescription=prescription,
                patient=prescription.patient,
                **medicine_data
            )

        return prescription


class PrescriptionDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_mobile = serializers.CharField(source='patient.mobile_number', read_only=True)
    medicines = MedicineSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'
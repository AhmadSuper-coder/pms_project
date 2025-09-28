from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from datetime import date, timedelta
from .models import Prescription, Medicine
from .serializers import (
    PrescriptionSerializer,
    PrescriptionCreateSerializer,
    PrescriptionDetailSerializer,
    MedicineSerializer
)
from backend_apps.patient.models import Patient
from backend_apps.patient.serializers import PatientSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for Prescriptions:

    GET /api/prescription/ # List all prescriptions for doctor
    POST /api/prescription/ # Create new prescription (doctor auto-set)
    GET /api/prescription/{id}/ # Get specific prescription
    PUT /api/prescription/{id}/ # Update prescription
    PATCH /api/prescription/{id}/ # Partial update prescription
    DELETE /api/prescription/{id}/ # Delete prescription
    """
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__full_name', 'patient__mobile_number', 'special_instructions']
    filterset_fields = ['patient', 'follow_up_date']
    ordering_fields = ['created_at', 'updated_at', 'follow_up_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """Only prescriptions for patients of the logged-in doctor"""
        return Prescription.objects.filter(
            patient__doctor=self.request.user
        ).select_related('patient', 'doctor').prefetch_related('medicines')

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return PrescriptionCreateSerializer
        elif self.action == 'retrieve':
            return PrescriptionDetailSerializer
        return PrescriptionSerializer

    def perform_create(self, serializer):
        """Auto-set doctor from authenticated user when creating a prescription"""
        serializer.save(doctor=self.request.user)

    def list(self, request, *args, **kwargs):
        """Custom list response with summary"""
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Prescriptions retrieved successfully',
                'prescriptions': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)

        # Calculate summary
        total_prescriptions = queryset.count()
        upcoming_followups = queryset.filter(
            follow_up_date__gte=date.today()
        ).count()
        overdue_followups = queryset.filter(
            follow_up_date__lt=date.today(),
            follow_up_date__isnull=False
        ).count()

        return Response({
            'success': True,
            'message': 'Prescriptions retrieved successfully',
            'count': total_prescriptions,
            'summary': {
                'total_prescriptions': total_prescriptions,
                'upcoming_followups': upcoming_followups,
                'overdue_followups': overdue_followups,
                'total_patients_treated': queryset.values('patient').distinct().count()
            },
            'prescriptions': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """Custom create response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'success': True,
            'message': 'Prescription created successfully',
            'prescription': serializer.data
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Custom retrieve with additional info"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            'success': True,
            'prescription': serializer.data
        })

    def update(self, request, *args, **kwargs):
        """Custom update response"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'success': True,
            'message': 'Prescription updated successfully',
            'prescription': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """Custom delete response"""
        instance = self.get_object()
        prescription_info = f"Prescription for {instance.patient.full_name} dated {instance.created_at.date()}"
        self.perform_destroy(instance)

        return Response({
            'success': True,
            'message': f'{prescription_info} deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def detailed_by_pk(self, request, pk=None):
        """
        Get detailed prescription information with patient history and medicines
        Usage: GET /api/prescription/1/detailed_by_pk/
        """
        try:
            prescription = self.get_object()

            # Get prescription basic info
            prescription_serializer = PrescriptionDetailSerializer(prescription)

            # Get patient info
            patient_serializer = PatientSerializer(prescription.patient)

            # Get patient's prescription history
            patient_prescriptions = Prescription.objects.filter(
                patient=prescription.patient,
                patient__doctor=self.request.user
            ).order_by('-created_at')

            patient_prescription_history = PrescriptionSerializer(patient_prescriptions, many=True)

            # Get all medicines for this prescription
            medicines = prescription.medicines.all()
            medicines_serializer = MedicineSerializer(medicines, many=True)

            # Calculate patient prescription summary
            total_prescriptions = patient_prescriptions.count()
            total_medicines = Medicine.objects.filter(
                prescription__in=patient_prescriptions
            ).count()

            return Response({
                'success': True,
                'prescription_id': prescription.id,
                'prescription_information': {
                    'id': prescription.id,
                    'date_issued': prescription.created_at,
                    'special_instructions': prescription.special_instructions,
                    'follow_up_date': prescription.follow_up_date,
                    'medicines_count': medicines.count(),
                    'created_at': prescription.created_at,
                    'updated_at': prescription.updated_at
                },
                'patient_information': {
                    'id': prescription.patient.id,
                    'full_name': prescription.patient.full_name,
                    'mobile_number': prescription.patient.mobile_number,
                    'age': prescription.patient.age,
                    'gender': prescription.patient.get_gender_display() if prescription.patient.gender else None,
                    'known_allergies': prescription.patient.known_allergies,
                    'medical_history': prescription.patient.medical_history
                },
                'medicines': {
                    'count': medicines.count(),
                    'list': medicines_serializer.data
                },
                'prescription_summary': {
                    'total_prescriptions': total_prescriptions,
                    'total_medicines_prescribed': total_medicines,
                    'last_prescription_date': patient_prescriptions.first().created_at if patient_prescriptions.exists() else None,
                    'next_follow_up': prescription.follow_up_date,
                    'follow_up_status': 'upcoming' if prescription.follow_up_date and prescription.follow_up_date >= date.today() else 'overdue' if prescription.follow_up_date else 'no_followup'
                },
                'prescription_history': {
                    'count': total_prescriptions,
                    'list': patient_prescription_history.data[:5]  # Last 5 prescriptions
                }
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get all prescriptions for a specific patient"""
        patient_id = request.query_params.get('patient_id')

        if not patient_id:
            return Response({
                'success': False,
                'error': 'patient_id query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ensure patient belongs to current doctor
            patient = Patient.objects.get(id=patient_id, doctor=request.user)
        except Patient.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Patient not found or you do not have access'
            }, status=status.HTTP_404_NOT_FOUND)

        prescriptions = self.get_queryset().filter(patient=patient)
        serializer = self.get_serializer(prescriptions, many=True)

        # Calculate patient prescription summary
        total_medicines = Medicine.objects.filter(
            prescription__in=prescriptions
        ).count()

        return Response({
            'success': True,
            'patient_name': patient.full_name,
            'patient_mobile': patient.mobile_number,
            'prescriptions_count': prescriptions.count(),
            'summary': {
                'total_prescriptions': prescriptions.count(),
                'total_medicines': total_medicines,
                'last_visit': prescriptions.first().created_at if prescriptions.exists() else None,
                'next_follow_up': prescriptions.filter(
                    follow_up_date__gte=date.today()
                ).first().follow_up_date if prescriptions.filter(
                    follow_up_date__gte=date.today()
                ).exists() else None
            },
            'prescriptions': serializer.data
        })

    @action(detail=False, methods=['get'])
    def followups(self, request):
        """Get prescriptions with upcoming or overdue follow-ups"""
        filter_type = request.query_params.get('filter', 'upcoming')  # upcoming, overdue, all

        if filter_type == 'upcoming':
            prescriptions = self.get_queryset().filter(
                follow_up_date__gte=date.today()
            ).order_by('follow_up_date')
        elif filter_type == 'overdue':
            prescriptions = self.get_queryset().filter(
                follow_up_date__lt=date.today(),
                follow_up_date__isnull=False
            ).order_by('follow_up_date')
        else:
            prescriptions = self.get_queryset().filter(
                follow_up_date__isnull=False
            ).order_by('follow_up_date')

        serializer = self.get_serializer(prescriptions, many=True)

        return Response({
            'success': True,
            'filter_type': filter_type,
            'count': prescriptions.count(),
            'followups': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get prescriptions summary for the doctor"""
        queryset = self.get_queryset()

        # Overall statistics
        total_prescriptions = queryset.count()
        total_patients = queryset.values('patient').distinct().count()
        total_medicines = Medicine.objects.filter(prescription__in=queryset).count()

        # Follow-up statistics
        upcoming_followups = queryset.filter(follow_up_date__gte=date.today()).count()
        overdue_followups = queryset.filter(
            follow_up_date__lt=date.today(),
            follow_up_date__isnull=False
        ).count()

        # Recent prescriptions
        recent_prescriptions = queryset.order_by('-created_at')[:5]
        recent_serializer = self.get_serializer(recent_prescriptions, many=True)

        # Most common medicines
        common_medicines = Medicine.objects.filter(
            prescription__in=queryset
        ).values('name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return Response({
            'success': True,
            'summary': {
                'total_prescriptions': total_prescriptions,
                'total_patients_treated': total_patients,
                'total_medicines_prescribed': total_medicines,
                'upcoming_followups': upcoming_followups,
                'overdue_followups': overdue_followups,
                'recent_prescriptions': recent_serializer.data,
                'common_medicines': list(common_medicines)
            }
        })

    @action(detail=True, methods=['post'])
    def add_medicine(self, request, pk=None):
        """Add medicine to existing prescription"""
        prescription = self.get_object()
        medicine_data = request.data

        medicine_serializer = MedicineSerializer(data=medicine_data)
        if medicine_serializer.is_valid():
            medicine_serializer.save(
                prescription=prescription,
                patient=prescription.patient
            )

            return Response({
                'success': True,
                'message': 'Medicine added successfully',
                'medicine': medicine_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': medicine_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)







# Add to the same views.py file

class MedicineViewSet(viewsets.ModelViewSet):
    """CRUD operations for individual medicines"""
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Medicine.objects.filter(
            prescription__patient__doctor=self.request.user
        ).select_related('prescription', 'patient')
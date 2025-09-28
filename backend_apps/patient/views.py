from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .models import Patient
from .serializers import PatientSerializer
from backend_apps.prescription.serializers import PrescriptionSerializer
from backend_apps.bills.serializers import BillSerializer
# from pms_backend.utils import get_user_id_from_jwt

class PatientViewSet(viewsets.ModelViewSet):

    """
        GET /api/patient/ # List all patients
        POST /api/patient/ # Create patient (doctor auto-set)
        GET /api/patient/{id}/ # Get specific patient
        PUT /api/patient/{id}/ # Update patient
        PUT /api/patient/{id}/ # Update patient
        DELETE /api/patient/{id}/ # Delete patient
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only active patients of logged-in doctor by default
        queryset = Patient.objects.filter(doctor=self.request.user)

        # Allow filtering by status via query parameter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)


        return queryset

    @action(detail=True, methods=['patch'])
    def activate(self, request, pk=None):
        """Activate a patient"""
        patient = self.get_object()
        patient.activate()
        serializer = self.get_serializer(patient)

        return Response({
            'success': True,
            'message': f'Patient {patient.full_name} has been activated',
            'patient': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        """Deactivate a patient"""
        patient = self.get_object()
        patient.deactivate()
        serializer = self.get_serializer(patient)

        return Response({
            'success': True,
            'message': f'Patient {patient.full_name} has been deactivated',
            'patient': serializer.data
        })

    def perform_create(self, serializer):
        # Auto-set doctor from authenticated user when creating a patient
        serializer.save(doctor=self.request.user)

    @action(detail=True, methods=['get'])
    def detailed_by_pk(self, request, pk=None):
        """
        Get detailed patient information organized by sections
        Usage: GET /api/patient/1/detailed_by_pk/
        """
        try:
            patient = self.get_object()  # This automatically filters by current doctor

            # Get related data
            prescriptions = patient.prescriptions.all().order_by('-created_at')
            prescriptions_serializer = PrescriptionSerializer(prescriptions, many=True)

            bills = patient.bills.all().order_by('-created_at')
            bills_serializer = BillSerializer(bills, many=True)

            # Get documents if available
            documents = []
            documents_count = 0
            try:
                from backend_apps.document.models import Document
                from backend_apps.document.serializers import DocumentSerializer

                patient_documents = Document.objects.filter(patient=patient).order_by('-created_at')
                documents_serializer = DocumentSerializer(patient_documents, many=True)
                documents = documents_serializer.data
                documents_count = patient_documents.count()
            except ImportError:
                # Document app not available
                pass

            return Response({
                'success': True,
                'patient_id': patient.id,
                'basic_information': {
                    'full_name': patient.full_name,
                    'age': patient.age,
                    'gender': patient.get_gender_display() if patient.gender else None,
                    'gender_value': patient.gender,
                    'status': patient.get_status_display(),
                    'status_value': patient.status,
                    'created_on': patient.created_at,
                    'last_updated': patient.updated_at
                },
                'contact_information': {
                    'mobile_number': patient.mobile_number,
                    'email': patient.email,
                    'address': patient.address
                },
                'personal_details': {
                    'emergency_contact': patient.emergency_contact,
                    'created_on': patient.created_at
                },
                'medical_history': {
                    'medical_history': patient.medical_history,
                    'known_allergies': patient.known_allergies,
                    'lifestyle_information': patient.lifestyle_information
                },
                'documents': {
                    'count': documents_count,
                    'list': documents
                },
                'prescriptions': {
                    'count': prescriptions.count(),
                    'total_visits': prescriptions.count(),
                    'last_visit': prescriptions.first().created_at if prescriptions.exists() else None,
                    'next_follow_up': prescriptions.filter(
                        follow_up_date__isnull=False
                    ).first().follow_up_date if prescriptions.filter(
                        follow_up_date__isnull=False
                    ).exists() else None,
                    'list': prescriptions_serializer.data
                },
                'billing': {
                    'count': bills.count(),
                    'total_amount': sum(float(bill.amount) for bill in bills if bill.amount),
                    'paid_bills': bills.filter(status='paid').count(),
                    'pending_bills': bills.filter(status='pending').count(),
                    'overdue_bills': bills.filter(status='overdue').count(),
                    'last_bill_date': bills.first().date if bills.exists() else None,
                    'list': bills_serializer.data
                }
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # Custom action: get appointments
    # @action(detail=True, methods=["get"])
    # def appointments(self, request, pk=None):
    #     patient = self.get_object()
    #     appointments = patient.appointment_set.all()  # or reverse relation
    #     serializer = AppointmentSerializer(appointments, many=True)
    #     return Response(serializer.data)

    # Custom action: get prescriptions
    @action(detail=True, methods=["get"])
    def prescriptions(self, request, pk=None):
        patient = self.get_object()
        prescriptions = patient.prescription_set.all()
        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)

    # Custom action: get bills
    @action(detail=True, methods=["get"])
    def bills(self, request, pk=None):
        patient = self.get_object()
        bills = patient.bill_set.all()
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)

    # Custom action: send info via WhatsApp/SMS/Email
    @action(detail=True, methods=["post"])
    def send_info(self, request, pk=None):
        patient = self.get_object()
        method = request.data.get("method")
        message = request.data.get("message")
        # implement sending logic here
        return Response({"message": f"Sent via {method}"})
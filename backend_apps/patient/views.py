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
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only patients of logged-in doctor
        return Patient.objects.filter(doctor=self.request.user)


    def perform_create(self, serializer):
        # Auto-set doctor from authenticated user when creating a patient
        serializer.save(doctor=self.request.user)


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
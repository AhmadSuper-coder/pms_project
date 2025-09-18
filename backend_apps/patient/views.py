from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer


class IsDoctorOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Patient):
        return obj.doctor_id == request.user.id

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctorOwner]

    def get_queryset(self):
        return Patient.objects.filter(doctor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)

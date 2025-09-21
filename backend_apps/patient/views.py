from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q

from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(ModelViewSet):
    """
    ViewSet for managing patients.
    
    Provides CRUD operations for patients with filtering and search capabilities.
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email', 'phone', 'address']
    ordering_fields = ['full_name', 'created_at', 'updated_at']
    ordering = ['full_name']

    def get_queryset(self):
        """Return patients filtered by the authenticated doctor."""
        return Patient.objects.filter(doctor=self.request.user)

    def perform_create(self, serializer):
        """Set the doctor to the authenticated user when creating a patient."""
        serializer.save(doctor=self.request.user)

    def get_serializer_context(self):
        """Add request context to serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Custom search action for advanced patient filtering.
        
        Query parameters:
        - q: Search term for full name, email, or phone
        - age_min: Minimum age filter
        - age_max: Maximum age filter
        - gender: Filter by gender
        """
        queryset = self.get_queryset()
        
        # Text search
        search_term = request.query_params.get('q', '')
        if search_term:
            queryset = queryset.filter(
                Q(full_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )
        
        # Age filtering
        age_min = request.query_params.get('age_min')
        age_max = request.query_params.get('age_max')
        if age_min:
            queryset = queryset.filter(age__gte=int(age_min))
        if age_max:
            queryset = queryset.filter(age__lte=int(age_max))
        
        # Gender filtering
        gender = request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get a summary of patient information."""
        patient = self.get_object()
        return Response({
            'id': patient.id,
            'full_name': patient.full_name,
            'age': patient.age,
            'gender': patient.gender,
            'phone': patient.phone,
            'email': patient.email,
            'total_documents': patient.documents.count(),
            'last_visit': patient.updated_at,
        })

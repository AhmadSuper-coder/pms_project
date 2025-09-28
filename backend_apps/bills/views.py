from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from .models import Bill
from .serializers import BillSerializer
from backend_apps.patient.models import Patient
from backend_apps.patient.serializers import PatientSerializer


class BillViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for Bills:

    GET /api/bills/ # List all bills for doctor
    POST /api/bills/ # Create new bill (doctor auto-set)
    GET /api/bills/{id}/ # Get specific bill
    PUT /api/bills/{id}/ # Update bill
    PATCH /api/bills/{id}/ # Partial update bill
    DELETE /api/bills/{id}/ # Delete bill
    """
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__full_name', 'patient__mobile_number', 'notes']
    filterset_fields = ['status', 'payment_method', 'patient']
    ordering_fields = ['amount', 'date', 'created_at', 'updated_at']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        """Only bills for patients of the logged-in doctor"""
        queryset = Bill.objects.filter(doctor=self.request.user).select_related('patient', 'doctor')

        # Allow filtering by status via query parameter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        """Auto-set doctor from authenticated user when creating a bill"""
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
                'message': 'Bills retrieved successfully',
                'bills': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)

        # Calculate summary
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        paid_count = queryset.filter(status='paid').count()
        pending_count = queryset.filter(status='pending').count()
        overdue_count = queryset.filter(status='overdue').count()

        return Response({
            'success': True,
            'message': 'Bills retrieved successfully',
            'count': queryset.count(),
            'summary': {
                'total_amount': float(total_amount),
                'paid_bills': paid_count,
                'pending_bills': pending_count,
                'overdue_bills': overdue_count
            },
            'bills': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """Custom create response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'success': True,
            'message': 'Bill created successfully',
            'bill': serializer.data
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Custom retrieve with additional info"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Get patient info
        patient_serializer = PatientSerializer(instance.patient)

        return Response({
            'success': True,
            'bill': serializer.data,
            'patient_info': patient_serializer.data
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
            'message': 'Bill updated successfully',
            'bill': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """Custom delete response"""
        instance = self.get_object()
        bill_info = f"Bill #{instance.id} for {instance.patient.full_name}"
        self.perform_destroy(instance)

        return Response({
            'success': True,
            'message': f'{bill_info} deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def detailed_by_pk(self, request, pk=None):
        """
        Get detailed bill information with patient and payment history
        Usage: GET /api/bills/1/detailed_by_pk/
        """
        try:
            bill = self.get_object()

            # Get bill basic info
            bill_serializer = self.get_serializer(bill)

            # Get patient info
            patient_serializer = PatientSerializer(bill.patient)

            # Get patient's bill history
            patient_bills = Bill.objects.filter(
                patient=bill.patient,
                doctor=self.request.user
            ).order_by('-date')

            patient_bill_history = self.get_serializer(patient_bills, many=True)

            # Calculate patient billing summary
            total_bills = patient_bills.count()
            total_amount = patient_bills.aggregate(total=Sum('amount'))['total'] or 0
            paid_amount = patient_bills.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
            pending_amount = patient_bills.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
            overdue_amount = patient_bills.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0

            return Response({
                'success': True,
                'bill_id': bill.id,
                'bill_information': {
                    'id': bill.id,
                    'amount': float(bill.amount),
                    'date': bill.date,
                    'status': bill.get_status_display(),
                    'status_value': bill.status,
                    'payment_method': bill.get_payment_method_display(),
                    'payment_method_value': bill.payment_method,
                    'notes': bill.notes,
                    'created_at': bill.created_at,
                    'updated_at': bill.updated_at
                },
                'patient_information': {
                    'id': bill.patient.id,
                    'full_name': bill.patient.full_name,
                    'mobile_number': bill.patient.mobile_number,
                    'email': bill.patient.email,
                    'status': bill.patient.get_status_display()
                },
                'billing_summary': {
                    'total_bills': total_bills,
                    'total_amount': float(total_amount),
                    'paid_amount': float(paid_amount),
                    'pending_amount': float(pending_amount),
                    'overdue_amount': float(overdue_amount),
                    'balance_due': float(total_amount - paid_amount),
                    'last_payment_date': patient_bills.filter(status='paid').first().date if patient_bills.filter(
                        status='paid').exists() else None
                },
                'bill_history': {
                    'count': total_bills,
                    'list': patient_bill_history.data
                }
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def mark_paid(self, request, pk=None):
        """Mark a bill as paid"""
        bill = self.get_object()
        payment_method = request.data.get('payment_method', bill.payment_method)

        bill.status = 'paid'
        bill.payment_method = payment_method
        bill.save(update_fields=['status', 'payment_method', 'updated_at'])

        serializer = self.get_serializer(bill)
        return Response({
            'success': True,
            'message': f'Bill #{bill.id} marked as paid',
            'bill': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def mark_pending(self, request, pk=None):
        """Mark a bill as pending"""
        bill = self.get_object()
        bill.status = 'pending'
        bill.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(bill)
        return Response({
            'success': True,
            'message': f'Bill #{bill.id} marked as pending',
            'bill': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def mark_overdue(self, request, pk=None):
        """Mark a bill as overdue"""
        bill = self.get_object()
        bill.status = 'overdue'
        bill.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(bill)
        return Response({
            'success': True,
            'message': f'Bill #{bill.id} marked as overdue',
            'bill': serializer.data
        })

    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get all bills for a specific patient"""
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

        bills = self.get_queryset().filter(patient=patient)
        serializer = self.get_serializer(bills, many=True)

        # Calculate patient bill summary
        total_amount = bills.aggregate(total=Sum('amount'))['total'] or 0
        paid_amount = bills.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        pending_amount = bills.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'success': True,
            'patient_name': patient.full_name,
            'patient_mobile': patient.mobile_number,
            'bills_count': bills.count(),
            'summary': {
                'total_amount': float(total_amount),
                'paid_amount': float(paid_amount),
                'pending_amount': float(pending_amount),
                'balance_due': float(total_amount - paid_amount)
            },
            'bills': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get bills summary for the doctor"""
        queryset = self.get_queryset()

        # Overall statistics
        total_bills = queryset.count()
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0

        # Status breakdown
        status_stats = []
        for choice in Bill.Status.choices:
            status_key = choice[0]
            status_label = choice[1]
            bills = queryset.filter(status=status_key)
            count = bills.count()
            amount = bills.aggregate(total=Sum('amount'))['total'] or 0
            status_stats.append({
                'status': status_key,
                'label': status_label,
                'count': count,
                'amount': float(amount)
            })

        # Recent bills
        recent_bills = queryset.order_by('-created_at')[:5]
        recent_serializer = self.get_serializer(recent_bills, many=True)

        return Response({
            'success': True,
            'summary': {
                'total_bills': total_bills,
                'total_amount': float(total_amount),
                'status_breakdown': status_stats,
                'recent_bills': recent_serializer.data
            }
        })
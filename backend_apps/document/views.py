import uuid
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .exceptions import DocumentException, document_exception
from .models import Document
from backend_apps.patient.models import Patient
from .serializers import DocumentSerializer
from .gcs import generate_presigned_upload_url, generate_presigned_download_url

def _gcs_client():
    try:
        from google.cloud import storage
    except Exception as e:
        raise RuntimeError("google-cloud-storage is not installed") from e
    return storage.Client()


class GcsSignUploadUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            filename = request.data.get("filename")
            content_type = request.data.get("content_type")
            size_bytes = request.data.get("size_bytes")
            patient_id = request.data.get("patient_id")
            document_type = request.data.get("document_type")
            description = request.data.get("description")
            if not filename or not content_type:
                raise DocumentException(document_exception.FILE_INFO_REQUIRED)
            if not patient_id:
                raise DocumentException(document_exception.PATIENT_ID_REQUIRED)

            # "document.pdf", "application/pdf"
            signed_url, unique_file_key, expires_in, method= generate_presigned_upload_url(filename, content_type)

            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                raise DocumentException(document_exception.PATIENT_NOT_FOUND)

            doc = Document.objects.create(
                owner=request.user if request.user.is_authenticated else None,
                patient=patient,
                filename=filename,
                content_type=content_type,
                gcs_key=unique_file_key,
                size_bytes=size_bytes or None,
                document_type=document_type or None,
                is_uploaded=False,
                description=description or None,
            )

            return Response(
                {
                    "upload_url": signed_url,
                    "method": method,
                    "headers": {"Content-Type": content_type},
                    "key": unique_file_key,
                    "document_id": doc.id,
                    "expires_in": expires_in,
                }
            )

        except DocumentException as e:
            document_exception.response(e.args[0], __name__)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        document_id = request.data.get("document_id")
        if not document_id:
            return Response({"detail": "document_id required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doc = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        # Optionally: verify blob existence or metadata here.
        doc.is_uploaded = True
        doc.save(update_fields=["is_uploaded", "updated_at"])

        # Return a GET URL for later access (signed GET) # Return a GET URL for later access (signed GET)
        try:
            download_url, download_expires_in = generate_presigned_download_url(doc.gcs_key)

        except DocumentException as e:
            return Response(
                {"detail": f"Failed to generate download URL: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "status": True,
                "document": {
                    "id": doc.id,
                    "filename": doc.filename,
                    "content_type": doc.content_type,
                    "key": doc.gcs_key,
                },
                "download_url": download_url,
                "download_expires_in": download_expires_in,
            }
        )


class PatientDocumentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id: int):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        gcs_cfg = get_gcs_settings()
        bucket_name = gcs_cfg['bucket']
        expires_in = gcs_cfg['get_expire_seconds']

        documents = Document.objects.filter(patient=patient).order_by('-created_at')
        items = []
        for d in documents:
            url = generate_signed_get_url(bucket_name, d.gcs_key, expires_in) if d.is_uploaded else None
            items.append({
                "id": d.id,
                "filename": d.filename,
                "content_type": d.content_type,
                "document_type": d.document_type,
                "size_bytes": d.size_bytes,
                "is_uploaded": d.is_uploaded,
                "created_at": d.created_at,
                "download_url": url,
                "download_expires_in": expires_in if url else None,
            })

        return Response({"patient_id": patient.id, "documents": items})


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id: int):
        try:
            d = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        gcs_cfg = get_gcs_settings()
        bucket_name = gcs_cfg['bucket']
        expires_in = gcs_cfg['get_expire_seconds']
        url = generate_signed_get_url(bucket_name, d.gcs_key, expires_in) if d.is_uploaded else None

        return Response({
            "id": d.id,
            "filename": d.filename,
            "content_type": d.content_type,
            "document_type": d.document_type,
            "size_bytes": d.size_bytes,
            "is_uploaded": d.is_uploaded,
            "created_at": d.created_at,
            "download_url": url,
            "download_expires_in": expires_in if url else None,
        })


class DocumentViewSet(ModelViewSet):
    """
    ViewSet for managing documents.
    
    Provides CRUD operations for documents with filtering and search capabilities.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['filename', 'document_type']
    ordering_fields = ['filename', 'created_at', 'updated_at', 'size_bytes']
    ordering = ['-created_at']
    filterset_fields = ['patient', 'document_type', 'is_uploaded']

    def get_queryset(self):
        """Return documents filtered by the authenticated DocumentViewSetDocumentViewSetdoctor."""
        return Document.objects.filter(patient__doctor=self.request.user)

    def perform_create(self, serializer):
        """Set the owner to the authenticated user when creating a document."""
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        """Add request context to serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['get'])
    def download_url(self, request, pk=None):
        """Get a signed download URL for the document."""
        document = self.get_object()
        
        if not document.is_uploaded:
            return Response(
                {"detail": "Document not uploaded yet"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        gcs_cfg = get_gcs_settings()
        bucket_name = gcs_cfg['bucket']
        expires_in = gcs_cfg['get_expire_seconds']
        
        try:
            download_url = generate_signed_get_url(bucket_name, document.gcs_key, expires_in)
            return Response({
                'download_url': download_url,
                'expires_in': expires_in,
                'filename': document.filename
            })
        except Exception as e:
            return Response(
                {"detail": f"Failed to generate download URL: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get all documents for a specific patient."""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {"detail": "patient_id query parameter required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            patient = Patient.objects.get(id=patient_id, doctor=request.user)
        except Patient.DoesNotExist:
            return Response(
                {"detail": "Patient not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        documents = self.get_queryset().filter(patient=patient)
        
        # Apply pagination
        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get document statistics for the authenticated doctor."""
        queryset = self.get_queryset()
        
        stats = {
            'total_documents': queryset.count(),
            'uploaded_documents': queryset.filter(is_uploaded=True).count(),
            'pending_documents': queryset.filter(is_uploaded=False).count(),
            'total_size_bytes': sum(d.size_bytes for d in queryset.filter(is_uploaded=True) if d.size_bytes),
            'documents_by_type': {}
        }
        
        # Count by document type
        for doc_type in queryset.values_list('document_type', flat=True).distinct():
            if doc_type:
                stats['documents_by_type'][doc_type] = queryset.filter(document_type=doc_type).count()
        
        return Response(stats)


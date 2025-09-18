import uuid
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from .models import Document
from backend_apps.patient.models import Patient
from .gcs import get_gcs_settings, build_upload_key, generate_signed_put_url, generate_signed_get_url
from .serializers import DocumentSerializer


def _gcs_client():
    try:
        from google.cloud import storage
    except Exception as e:
        raise RuntimeError("google-cloud-storage is not installed") from e
    return storage.Client()


class GcsSignUploadUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        filename = request.data.get("filename")
        content_type = request.data.get("content_type")
        size_bytes = request.data.get("size_bytes")
        patient_id = request.data.get("patient_id")
        document_type = request.data.get("document_type")
        if not filename or not content_type:
            return Response({"detail": "filename and content_type required"}, status=status.HTTP_400_BAD_REQUEST)
        if not patient_id:
            return Response({"detail": "patient_id required"}, status=status.HTTP_400_BAD_REQUEST)

        gcs_cfg = get_gcs_settings()
        bucket_name = gcs_cfg['bucket']
        if not bucket_name:
            return Response({"detail": "GCS bucket not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        unique_key = build_upload_key(filename, gcs_cfg['upload_prefix'])
        expires_in = gcs_cfg['put_expire_seconds']
        method = "PUT"
        signed_url = generate_signed_put_url(bucket_name, unique_key, content_type, expires_in)

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        doc = Document.objects.create(
            owner=request.user if request.user.is_authenticated else None,
            patient=patient,
            filename=filename,
            content_type=content_type,
            gcs_key=unique_key,
            size_bytes=size_bytes or None,
            document_type=document_type or None,
            is_uploaded=False,
        )

        return Response(
            {
                "upload_url": signed_url,
                "method": method,
                "headers": {"Content-Type": content_type},
                "key": unique_key,
                "document_id": doc.id,
                "expires_in": expires_in,
            }
        )


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

        # Return a GET URL for later access (signed GET)
        gcs_cfg = get_gcs_settings()
        bucket_name = gcs_cfg['bucket']
        get_expires_in = gcs_cfg['get_expire_seconds']
        download_url = generate_signed_get_url(bucket_name, doc.gcs_key, get_expires_in)

        return Response(
            {
                "detail": "Upload confirmed",
                "document": {
                    "id": doc.id,
                    "filename": doc.filename,
                    "content_type": doc.content_type,
                    "key": doc.gcs_key,
                },
                "download_url": download_url,
                "download_expires_in": get_expires_in,
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


class DocumentCRUDView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, document_id=None):
        if document_id is None:
            qs = Document.objects.filter(patient__doctor=request.user)
            patient_id = request.query_params.get('patient_id')
            if patient_id:
                qs = qs.filter(patient_id=patient_id)
            data = DocumentSerializer(qs.order_by('-created_at'), many=True).data
            return Response({"results": data})
        try:
            d = Document.objects.get(id=document_id, patient__doctor=request.user)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentSerializer(d).data)

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        doc = serializer.save(owner=request.user)
        return Response(DocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

    def patch(self, request, document_id=None):
        if document_id is None:
            return Response({"detail": "document_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            d = Document.objects.get(id=document_id, patient__doctor=request.user)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentSerializer(d, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, document_id=None):
        if document_id is None:
            return Response({"detail": "document_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            d = Document.objects.get(id=document_id, patient__doctor=request.user)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        d.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


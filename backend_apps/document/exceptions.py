# backend_apps/document/exceptions.py
from non_django.error_handling.exceptions import GlobalException

class DocumentException(GlobalException):
    FILE_INFO_REQUIRED = {0: "Filename and content_type are required."}
    PATIENT_ID_REQUIRED = {1: "Patient ID is required."}
    BUCKET_NOT_CONFIGURED = {2: "GCS bucket not configured."}
    PATIENT_NOT_FOUND = {3: "Patient not found."}

document_exception = DocumentException()

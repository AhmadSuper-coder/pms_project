from google.api_core.gapic_v1 import method

from backend_apps.document.gcs import get_gcs_settings, build_upload_key, generate_signed_put_url, generate_signed_get_url
from backend_apps.document.exceptions import DocumentException,document_exception

def generate_presigned_upload_url(filename: str, content_type: str) -> tuple[str, str, int, str]:
    """
    Generate a presigned URL for uploading a file to GCS.

    Args:
        filename: The original filename
        content_type: The MIME type of the file

    Returns:
        A tuple of (signed_url, unique_key)

    Raises:
        DocumentException: If GCS bucket is not configured
    """
    gcs_cfg = get_gcs_settings()
    bucket_name = gcs_cfg['bucket']
    method = "PUT"

    if not bucket_name:
        raise DocumentException(document_exception.BUCKET_NOT_CONFIGURED)

    unique_key = build_upload_key(filename, gcs_cfg['upload_prefix'])
    expires_in = int(gcs_cfg['put_expire_seconds'])

    signed_url = generate_signed_put_url(bucket_name, unique_key, content_type, expires_in)

    return signed_url, unique_key, expires_in, method
import os
import uuid
from datetime import timedelta
from typing import Dict
from decouple import config
from google.cloud import storage
from backend_apps.document.exceptions import DocumentException,document_exception
from non_django.error_handling.exceptions import GlobalException


def get_gcs_settings() -> Dict[str, str]:
    bucket = config('GCS_BUCKET_NAME', default='')
    upload_prefix = config('GCS_UPLOAD_PREFIX', default='uploads/')
    put_expire_seconds = config('GCS_SIGNED_URL_EXPIRE_SECONDS', default=30 * 60, cast=int)
    get_expire_seconds = config('GCS_SIGNED_GET_EXPIRE_SECONDS', default=60 * 60, cast=int)
    return {
        'bucket': bucket,
        'upload_prefix': upload_prefix,
        'put_expire_seconds': put_expire_seconds,
        'get_expire_seconds': get_expire_seconds,
    }


def get_client():
    # Get credentials path from environment
    credentials_path = config('GOOGLE_APPLICATION_CREDENTIALS', default=None)

    if credentials_path and os.path.exists(credentials_path):
        return storage.Client.from_service_account_json(credentials_path)
    else:
        # Fallback to default credentials
        return storage.Client()
    return storage.Client()


def build_upload_key(filename: str, upload_prefix: str) -> str:
    return f"{upload_prefix}{uuid.uuid4()}-{filename}"


def generate_signed_put_url(bucket_name: str, key: str, content_type: str, expire_seconds: int) -> str:
    client = get_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(key)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(seconds=expire_seconds),
        method="PUT",
        content_type=content_type,
    )


def generate_signed_get_url(bucket_name: str, key: str, expire_seconds: int) -> str:
    client = get_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(key)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(seconds=expire_seconds),
        method="GET",
    )



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
    try:
        gcs_cfg = get_gcs_settings()
        bucket_name = gcs_cfg['bucket']
        method = "PUT"

        if not bucket_name:
            raise DocumentException(document_exception.BUCKET_NOT_CONFIGURED)

        unique_key = build_upload_key(filename, gcs_cfg['upload_prefix'])
        expires_in = int(gcs_cfg['put_expire_seconds'])

        signed_url = generate_signed_put_url(bucket_name, unique_key, content_type, expires_in)

        return signed_url, unique_key, expires_in, method

    except DocumentException as e:
        GlobalException.print_exception_details_info(e)
        raise e


def generate_presigned_download_url(gcs_key: str) -> tuple[str, int]:
    """
    Generate a presigned URL for downloading a file from GCS.

    Args:
        gcs_key: The GCS key/path of the file to download

    Returns:
        A tuple of (download_url, expires_in_seconds)

    Raises:
        DocumentException: If GCS bucket is not configured
    """
    gcs_cfg = get_gcs_settings()
    bucket_name = gcs_cfg['bucket']

    if not bucket_name:
        raise DocumentException(document_exception.BUCKET_NOT_CONFIGURED)

    expires_in = int(gcs_cfg['get_expire_seconds'])
    download_url = generate_signed_get_url(bucket_name, gcs_key, expires_in)

    return download_url, expires_in
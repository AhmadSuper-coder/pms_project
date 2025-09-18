import os
import uuid
from datetime import timedelta
from typing import Dict

from django.conf import settings


def get_gcs_settings() -> Dict[str, str]:
    bucket = os.getenv('GCS_BUCKET_NAME', getattr(settings, 'GCS_BUCKET_NAME', ''))
    upload_prefix = os.getenv('GCS_UPLOAD_PREFIX', getattr(settings, 'GCS_UPLOAD_PREFIX', 'uploads/'))
    put_expire_seconds = int(os.getenv('GCS_SIGNED_URL_EXPIRE_SECONDS', getattr(settings, 'GCS_SIGNED_URL_EXPIRE_SECONDS', 15 * 60)))
    get_expire_seconds = int(os.getenv('GCS_SIGNED_GET_EXPIRE_SECONDS', getattr(settings, 'GCS_SIGNED_GET_EXPIRE_SECONDS', 60 * 60)))
    return {
        'bucket': bucket,
        'upload_prefix': upload_prefix,
        'put_expire_seconds': put_expire_seconds,
        'get_expire_seconds': get_expire_seconds,
    }


def get_client():
    from google.cloud import storage
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



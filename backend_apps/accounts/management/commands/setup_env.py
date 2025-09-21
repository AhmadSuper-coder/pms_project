"""
Management command to set up environment variables.
"""

import os
import secrets
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Set up environment variables for the PMS project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env-file',
            type=str,
            default='.env',
            help='Path to the .env file to create'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite existing .env file'
        )

    def handle(self, *args, **options):
        env_file = Path(options['env_file'])
        
        if env_file.exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING(f'{env_file} already exists. Use --force to overwrite.')
            )
            return

        # Generate secure secret keys
        secret_key = secrets.token_urlsafe(50)
        jwt_secret = secrets.token_urlsafe(32)

        env_content = f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=pms_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-database-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# JWT Settings
JWT_SECRET_KEY={jwt_secret}
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@pms.com

# OTP Configuration
OTP_CODE_LENGTH=6
OTP_TTL_SECONDS=300
OTP_MAX_ATTEMPTS=5
OTP_RESEND_COOLDOWN_SECONDS=30
OTP_EMAIL_SUBJECT=Your verification code
OTP_EMAIL_TEMPLATE=Your OTP code is: {{code}}
OTP_REQUIRE_PROVIDER_CONFIG=False

# Google Cloud Storage Configuration
GCS_BUCKET_NAME=your-gcs-bucket-name
GCS_UPLOAD_PREFIX=uploads/
GCS_SIGNED_URL_EXPIRE_SECONDS=900
GCS_SIGNED_GET_EXPIRE_SECONDS=3600
GCS_CREDENTIALS_PATH=path/to/your/credentials.json

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=True

# API Settings
API_PAGE_SIZE=20
API_MAX_PAGE_SIZE=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/django.log

# Cache (Redis - Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_BACKEND=django_redis.cache.RedisCache

# Security
SECURE_SSL_REDIRECT=False
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

# Development Tools
USE_DEBUG_TOOLBAR=True
ENABLE_PROFILING=False
"""

        # Create .env file
        env_file.write_text(env_content)
        
        # Create logs directory
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        self.stdout.write(
            self.style.SUCCESS(f'Environment file created at {env_file}')
        )
        self.stdout.write(
            self.style.SUCCESS('Please update the configuration values as needed.')
        )
        self.stdout.write(
            self.style.WARNING('IMPORTANT: Never commit the .env file to version control!')
        )

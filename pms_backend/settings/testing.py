"""
Testing settings for the PMS project.
"""

from .base import *

# Testing-specific settings
DEBUG = False

# Use in-memory database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations during testing for speed
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable caching during testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable logging during testing
LOGGING_CONFIG = None

# Testing-specific CORS settings
CORS_ALLOWED_ORIGINS = []

# Disable SSL redirect in testing
SECURE_SSL_REDIRECT = False

# Faster password hashing for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Test-specific OTP settings
OTP_TTL_SECONDS = 60  # 1 minute for faster testing
OTP_MAX_ATTEMPTS = 3  # Fewer attempts for testing

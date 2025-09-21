"""
Production settings for the PMS project.
"""

from .base import *

# Production-specific settings
DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS', default='DENY')
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)

# Production email backend
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# Production CORS settings (should be restricted to your frontend domains)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://yourdomain.com,https://www.yourdomain.com',
    cast=Csv()
)

# Production database (should be PostgreSQL)
DATABASES['default'].update({
    'ENGINE': 'django.db.backends.postgresql',
    'OPTIONS': {
        'sslmode': 'require',
    },
    'CONN_MAX_AGE': 60,
})

# Static files for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Production logging
LOGGING['handlers']['file']['filename'] = config('LOG_FILE', default='/var/log/django/pms.log')
LOGGING['handlers']['console']['level'] = 'WARNING'
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'

# Cache configuration (Redis recommended for production)
if config('REDIS_URL', default=''):
    CACHES = {
        'default': {
            'BACKEND': config('CACHE_BACKEND', default='django_redis.cache.RedisCache'),
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Session configuration for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour

# CSRF configuration for production
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

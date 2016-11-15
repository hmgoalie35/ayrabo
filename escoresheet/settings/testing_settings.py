import logging

from .settings import CACHES

# Django automatically sets DEBUG = False when running tests

logging.disable(logging.CRITICAL)

COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

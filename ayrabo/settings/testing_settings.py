import logging

from .settings import CACHES


# Django automatically sets DEBUG = False when running tests

logging.disable(logging.CRITICAL)

ALLOWED_HOSTS = '*'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

RUNNING_AUTOMATED_TESTS = True
GOOGLE_MAPS_API_KEY = 'dummykey'
SECRET_KEY = '6dlSWCSD5PHr9ygDEc9TRP0SpYpYCfegSD7Wx8nJFieCWOlDmY'

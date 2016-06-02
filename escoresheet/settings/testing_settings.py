# This file is inherting settings from local settings, see the last lines of settings.py
import logging

# Django automatically sets DEBUG = False when running tests

logging.disable(logging.CRITICAL)

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

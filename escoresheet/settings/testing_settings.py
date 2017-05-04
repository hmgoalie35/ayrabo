import logging
import os

from .settings import CACHES, DATABASES, BASE_DIR

# This file inherits settings from local_settings.py

logging.disable(logging.CRITICAL)

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'testdb.sqlite3'),
}

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

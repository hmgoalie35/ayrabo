import logging

logging.disable(logging.CRITICAL)

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

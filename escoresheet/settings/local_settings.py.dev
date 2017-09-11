from .settings import DATABASES, CACHES, REST_FRAMEWORK

DEBUG = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# https://docs.djangoproject.com/en/1.10/ref/databases/#caveats
DATABASES['default']['CONN_MAX_AGE'] = 0

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
}

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True,
    # Admin panel doesn't load jquery, so debug toolbar doesn't show...
}

# If INTERNAL_IPS becomes a problem, can override SHOW_TOOLBAR_CALLBACK function
# See https://django-debug-toolbar.readthedocs.io/en/stable/configuration.html#debug-toolbar-config
INTERNAL_IPS = ['127.0.0.1', 'localhost']

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].append('rest_framework.authentication.BasicAuthentication')

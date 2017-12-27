"""
Django settings for escoresheet project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import re
import sys

from django.urls import reverse_lazy

SITE_ID = 1

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ESCORESHEET_MODULE_ROOT = os.path.join(BASE_DIR, 'escoresheet')
NODE_MODULES_ROOT = os.path.join(BASE_DIR, 'node_modules')

ENV_SETTINGS = {}
dot_env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dot_env_path):
    with open(dot_env_path) as f:
        for line in f:
            k, v = line.strip().split('=')
            ENV_SETTINGS[k] = v

# Custom django apps are in apps/ directory, so add it to path
sys.path.append(os.path.join(BASE_DIR, 'apps'))

ADMINS = [('Harris Pittinsky', 'harris@pittinsky.com'), ]
MANAGERS = ADMINS

IGNORABLE_404_URLS = [
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
]

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 120

SECURE_SSL_REDIRECT = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SECURITY WARNING: keep the secret key used in production secret!
DEV_KEY = '9(31c+k9q8p++7a46ite17(@a3os_*)gg@+yqn4_5isb^v5=tr'
SECRET_KEY = ENV_SETTINGS.get('SECRET_KEY', DEV_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in ENV_SETTINGS.get('ALLOWED_HOSTS', '').split(',')]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # 3rd party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'behave_django',
    'crispy_forms',
    'debug_toolbar',
    'django_extensions',
    'django_filters',
    'localflavor',
    'rest_framework',
    'rest_framework.authtoken',
    'webpack_loader',

    # Custom apps
    'accounts.apps.AccountsConfig',
    'api.apps.ApiConfig',
    'coaches.apps.CoachesConfig',
    'common.apps.CommonConfig',
    'divisions.apps.DivisionsConfig',
    'games.apps.GamesConfig',
    'home.apps.HomeConfig',
    'leagues.apps.LeaguesConfig',
    'locations.apps.LocationsConfig',
    'managers.apps.ManagersConfig',
    'penalties.apps.PenaltiesConfig',
    'periods.apps.PeriodsConfig',
    'players.apps.PlayersConfig',
    'referees.apps.RefereesConfig',
    'seasons.apps.SeasonsConfig',
    'sports.apps.SportsConfig',
    'teams.apps.TeamsConfig',
    'userprofiles.apps.UserprofilesConfig',
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# NOTE: The ordering of the middleware is important, do not rearrange things unless you know what you are doing.
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'escoresheet.middleware.TranslationMiddleware',
    'escoresheet.middleware.TimezoneMiddleware',
    'accounts.middleware.AccountAndSportRegistrationCompleteMiddleware',
]

ROOT_URLCONF = 'escoresheet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # Django 1.11.x auto caches templates when DEBUG=False
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'escoresheet.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': ENV_SETTINGS.get('POSTGRES_DB'),
        'USER': ENV_SETTINGS.get('POSTGRES_USER'),
        'PASSWORD': ENV_SETTINGS.get('POSTGRES_PASSWORD'),
        'HOST': ENV_SETTINGS.get('POSTGRES_HOST', 'localhost'),
        'PORT': ENV_SETTINGS.get('POSTGRES_PORT', 5432),
        # For now leave as the default
        'CONN_MAX_AGE': 0,
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
        'TEST': {
            'CHARSET': 'UTF8'
        }
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher'
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

TIMEZONES = ['US/Alaska', 'US/Arizona', 'US/Central', 'US/Eastern', 'US/Hawaii', 'US/Mountain', 'US/Pacific', 'UTC']
COMMON_TIMEZONES = [(tz, tz) for tz in TIMEZONES]

USE_I18N = True

USE_L10N = True

USE_TZ = True

# TODO Make this a directory shared b/w deployments
DJANGO_LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(DJANGO_LOGS_DIR):
    os.mkdir(DJANGO_LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s %(pathname)s:%(lineno)d %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console_simple': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console_verbose': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file_verbose': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(DJANGO_LOGS_DIR, 'server_log.log'),
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True,
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
            'filters': ['require_debug_true'],
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console_simple'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_verbose', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        '': {
            'handlers': ['file_verbose', 'console_verbose'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

# Email address admins/managers receive mail from
# TODO update both of these
SERVER_EMAIL = 'no.reply@ess.com'
# Email address regular users receive mail from
DEFAULT_FROM_EMAIL = 'no.reply@ess.com'

# TODO configure this for prod
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ENV_SETTINGS.get('EMAIL_HOST')
EMAIL_HOST_USER = ENV_SETTINGS.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = ENV_SETTINGS.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = ENV_SETTINGS.get('EMAIL_PORT')
# Only set one of these to True at a time, if have problems try setting the other one
# EMAIL_USE_TLS = True
EMAIL_USE_SSL = ENV_SETTINGS.get('EMAIL_USE_SSL', 'false').lower() == 'true'
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# Http requests to STATIC_URL should be mapped to STATIC_ROOT

# The actual uri staticfiles are served from (localhost:8000/static/)
STATIC_URL = '/static/'
# The folder on the filesystem staticfiles are stored
STATIC_ROOT = os.path.join(BASE_DIR, 'build')
# Location to find extra static files (Django automatically looks in static/ subdirectories of all apps)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'dist/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Django all auth
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'  # This is `http` for local dev.
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.SignupForm',
    'login': 'accounts.forms.LoginForm',
    'reset_password': 'accounts.forms.PasswordResetForm',
    'reset_password_from_key': 'accounts.forms.PasswordResetFromKeyForm',
    'change_password': 'accounts.forms.ChangePasswordForm',
    'add_email': 'accounts.forms.AddEmailForm'
}
ACCOUNT_USERNAME_MIN_LENGTH = 1
ACCOUNT_SESSION_REMEMBER = False
ACCOUNT_USER_DISPLAY = lambda user: user.email

# Django auth settings
LOGIN_URL = reverse_lazy('account_login')
LOGIN_REDIRECT_URL = reverse_lazy('home')
LOGOUT_REDIRECT_URL = reverse_lazy('home')

TEST_RUNNER = 'redgreenunittest.django.runner.RedGreenDiscoverRunner'

FIXTURE_DIRS = [
    os.path.join(ESCORESHEET_MODULE_ROOT, 'fixtures')
]

API_VERSIONS = ['v1']
DEFAULT_VERSION = 'v1'

# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': DEFAULT_VERSION,
    'ALLOWED_VERSIONS': API_VERSIONS,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # For local development, BasicAuthentication is appended to this list in local_settings.dev.py
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

try:
    # Running in testing mode
    if len(sys.argv) > 1 and ('test' in sys.argv or 'behave' in sys.argv):
        from .testing_settings import *  # noqa
    else:
        # Running in dev mode
        from .local_settings import *  # noqa
except ImportError as e:
    # Running in production mode
    pass

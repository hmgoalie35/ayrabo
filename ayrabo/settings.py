"""
Generated by 'django-admin startproject' using Django 1.9.6.
"""

import logging
import os
import re
import sys

import environ
from django.urls import reverse_lazy


def create_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE_MODULES_DIR = os.path.join(BASE_DIR, 'node_modules')
APPS_DIR = os.path.join(BASE_DIR, 'apps')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

create_dir(LOGS_DIR)

ENV_FILE = os.path.join(BASE_DIR, '.env')
LOG_FILE = os.path.join(LOGS_DIR, 'ayrabo.log')

# Custom django apps are in apps/ directory, so add it to path
sys.path.append(APPS_DIR)

env = environ.Env()
env.read_env(ENV_FILE)

SITE_ID = 1

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)
RUNNING_AUTOMATED_TESTS = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
INTERNAL_IPS = env.list('INTERNAL_IPS')

ADMINS = [('Harris Pittinsky', 'support@ayrabo.com'), ]
MANAGERS = ADMINS
SUPPORT_CONTACT = {
    'email': 'support@ayrabo.com',
    'name': 'Harris Pittinsky'
}

IGNORABLE_404_URLS = [
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
]

# Caching
CACHES = {
    'default': env.cache('CACHE_URL')
}

# CSRF
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE')

# Security
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 120
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

AUTH_USER_MODEL = 'users.User'

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
    'django_object_actions',
    'easy_thumbnails',
    'localflavor',
    'rest_framework',
    'rest_framework.authtoken',
    'waffle',
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
    'organizations.apps.OrganizationsConfig',
    'penalties.apps.PenaltiesConfig',
    'periods.apps.PeriodsConfig',
    'players.apps.PlayersConfig',
    'referees.apps.RefereesConfig',
    'scorekeepers.apps.ScorekeepersConfig',
    'seasons.apps.SeasonsConfig',
    'sports.apps.SportsConfig',
    'teams.apps.TeamsConfig',
    'userprofiles.apps.UserprofilesConfig',
    'users.apps.UsersConfig',
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
    'ayrabo.middleware.TimezoneAndTranslationMiddleware',
    'accounts.middleware.UserProfileCompleteMiddleware',
    'waffle.middleware.WaffleMiddleware',
]

ROOT_URLCONF = 'ayrabo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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
                'common.context_processors.support_contact',
                'common.context_processors.sports_for_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'ayrabo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('POSTGRES_DB'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'HOST': env.str('POSTGRES_HOST'),
        'PORT': env.int('POSTGRES_PORT', default=5432),
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
            'filename': LOG_FILE,
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
SERVER_EMAIL = 'no.reply@ayrabo.com'
# Email address regular users receive mail from
DEFAULT_FROM_EMAIL = 'no.reply@ayrabo.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env.int('EMAIL_PORT')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [STATIC_DIR]

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'build/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = env.str('MEDIA_ROOT') or MEDIA_DIR

# Django all auth
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = env.str('ACCOUNT_DEFAULT_HTTP_PROTOCOL')
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

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures')
]

API_VERSIONS = ['v1']
DEFAULT_VERSION = 'v1'

# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': DEFAULT_VERSION,
    'ALLOWED_VERSIONS': API_VERSIONS,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].append('rest_framework.authentication.BasicAuthentication')

# Google Maps API
GOOGLE_MAPS_API_KEY = env.str('GOOGLE_MAPS_API_KEY')

# Easy thumbnails
THUMBNAIL_ALIASES = {
    # Project wide aliases
    '': {
        'sm': {'size': (30, 30)},
    }
}

THUMBNAIL_CACHE_DIMENSIONS = True
THUMBNAIL_DEBUG = env.bool('THUMBNAIL_DEBUG', default=DEBUG)
THUMBNAIL_NAMER = 'easy_thumbnails.namers.hashed'
THUMBNAIL_PRESERVE_EXTENSIONS = True
THUMBNAIL_SUBDIR = 'thumbnails'
THUMBNAIL_WIDGET_OPTIONS = THUMBNAIL_ALIASES.get('').get('sm')

# Waffle
WAFFLE_MAX_AGE = 1209600  # 2 weeks, same as SESSION_COOKIE_AGE

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True,
}

try:
    # Running in testing mode
    if len(sys.argv) > 1 and ('test' in sys.argv or 'behave' in sys.argv):
        PASSWORD_HASHERS = [
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ]
        INSTALLED_APPS.append('ayrabo.utils.testing')
        RUNNING_AUTOMATED_TESTS = True
        logging.disable(logging.CRITICAL)
except ImportError:
    # Running in production mode
    pass

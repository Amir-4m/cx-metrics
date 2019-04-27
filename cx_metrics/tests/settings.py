#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from datetime import timedelta
from kombu import Exchange, Queue


def gettext_noop(s):
    return s


# Celery settings
# http://docs.celeryproject.org/en/latest/configuration.html
# https://denibertovic.com/posts/celery-best-practices/
# http://celery.readthedocs.org/en/latest/userguide/monitoring.html

# Broker settings
BROKER_URL = 'amqp://guest:guest@localhost//'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ALWAYS_EAGER = True

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'default'

# http://docs.celeryproject.org/en/latest/configuration.html#celery-queues
CELERY_QUEUES = (
    Queue('default', Exchange('upkook', type='direct'), routing_key='default'),
)

CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

# http://docs.celeryproject.org/en/latest/configuration.html#celery-routes
# CELERY_ROUTES = {}

# Whether to store the task return values or not.
CELERY_IGNORE_RESULT = True

# If you still want to store errors, just not successful return values
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = False

# The backend used to store task results.
# CELERY_RESULT_BACKEND = ''

# Time (in seconds, or a timedelta object) for when after stored task
# tombstones will be deleted.
# CELERY_TASK_RESULT_EXPIRES = 0

# Django settings for upkook core project.

# The top directory for this project. Contains requirements/, manage.py,
# and README.rst, a cx_metrics directory with settings etc (see
# PROJECT_PATH), as well as a directory for each Django app added to this
# project.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# The directory with this project's templates, settings, urls, static dir,
# wsgi.py, fixtures, etc.
PROJECT_PATH = os.path.join(PROJECT_ROOT, 'cx_metrics')

DEBUG = True

TEST = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django-contrib.sqlite3',
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'fake-key'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/public/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'public', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/public/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public', 'static')

# Path to generated static files from JavaScript catalog
STATICI18N_ROOT = os.path.join(PROJECT_PATH, 'static', )

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files to collect
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False,
        'DIRS': (
            os.path.join(PROJECT_PATH, 'templates'),
        ),
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
            ),
            # List of callables that know how to import templates from
            # various sources.
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )
        }
    }
]

# List of compiled regular expression objects representing User-Agent strings
# that are not allowed to visit any page, system-wide.
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DISALLOWED_USER_AGENTS
DISALLOWED_USER_AGENTS = []

# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-APPEND_SLASH
APPEND_SLASH = False

# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-PREPEND_WWW
PREPEND_WWW = False

# A boolean that specifies whether to output the ETag header.
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-USE_ETAGS
USE_ETAGS = True

MIDDLEWARE = (
    # Enables session support.
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Adds a few conveniences for perfectionists (i.e. URL rewriting)
    'django.middleware.common.CommonMiddleware',
    # Adds protection against Cross Site Request Forgeries
    'django.middleware.csrf.CsrfViewMiddleware',
    # Adds the user attribute, representing the currently-logged-in user
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Enables cookie- and session-based message support.
    'django.contrib.messages.middleware.MessageMiddleware',
    # Simple clickjacking protection via the X-Frame-Options header.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

LOGIN_URL = '/login'

ROOT_URLCONF = 'cx_metrics.tests.urls'

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'fixtures'),
)

INSTALLED_APPS = (
    # Internal Django Apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',

    # Include app here if you use custom User
    'django_contrib.auth',

    # External Apps
    'django_extensions',
    # To configure Celery tasks from admin panel
    'django_celery_beat',
    'cities_light',
    'django.contrib.sites',
    'rest_framework',
    'corsheaders',

    # Project Apps
    'upkook_core.auth',
    'upkook_core.mail',
    'upkook_core.cities',
    'upkook_core.industries',
    'upkook_core.businesses',
    'upkook_core.teams',
    'upkook_core.customers',
    'cx_metrics.surveys',
    'cx_metrics.surveys.tests',
    'cx_metrics.nps',
)

# Set model for using in authentication
AUTH_USER_MODEL = 'django_auth.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'upkook_core.auth.authentication.TokenUserAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 24,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

# Django cors headers settings
CORS_ORIGIN_ALLOW_ALL = False

# cors domains
CORS_ORIGIN_WHITELIST = []

CORS_ORIGIN_REGEX_WHITELIST = []

CORS_ALLOW_METHODS = []

CORS_ALLOW_CREDENTIALS = True

SIMPLE_JWT = {
    # 5 minutes
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=60),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# django_cities_light
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['fa', 'en']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['IR']

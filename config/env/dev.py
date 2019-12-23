import os
# Never ever use "import *" except django configuration
# files like this one!
#
# If you write "import *" in any other python module and deploy
# such code in production, bugs will eat your business out!
from .base import *
# But in this *very unique scenario*... it works like a charm :)

# All environment common settings are defined in config/env/base.py
# This module overwrites dev env specific values.
ALLOWED_HOSTS = [
    'django-lessons.test', '*'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASS'],
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/eugen/var/'

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'django_all': {
            'class': 'logging.FileHandler',
            'filename': '/home/eugen/var/logging/django.log',
        },
        'lessons_all': {
            'class': 'logging.FileHandler',
            'filename': '/home/eugen/var/logging/lessons.log',
        },
    },
    'loggers': {
        # Logs only in development server (runserver command)
        # Works only with settings.DEBUG = True
        'django.server': {
            'handlers': ['django_all'],
            'level': 'DEBUG',
        },
        # Logs only 5xy and 4xx errors
        # settings.DEBUG does not change its behaviour
        'django.request': {
            'handlers': ['django_all'],
            'level': 'INFO',
        },
        # Logs database queries. Requires DEBUG level.
        # Works only with settings.DEBUG = True
        'django.db.backends': {
            'handlers': ['django_all'],
            'level': 'DEBUG',
        },
        'lessons': {
            'handlers': ['lessons_all'],
            'level': 'INFO',
        },
    },
}

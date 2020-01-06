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
INTERNAL_IPS = ('127.0.0.1',)

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

DEBUG = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/home/eugen/projects/Django-Lessons.js/static/',
]


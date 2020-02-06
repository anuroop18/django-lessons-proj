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

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_S3_CUSTOM_DOMAIN = os.environ['AWS_S3_CUSTOM_DOMAIN']

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
THUMBNAIL_DEFAULT_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATICFILES_DIRS = [
    '/home/eugen/projects/Django-Lessons.js/static/',
]

EMAIL_FROM = 'eugen@django-lessons.com'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/home/eugen/django_emails/'

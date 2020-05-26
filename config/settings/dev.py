import os

from .base import *  # noqa

# But in this *very unique scenario*... it works like a charm :)

# All environment common settings are defined in config/env/base.py
# This module overwrites dev env specific values.
ALLOWED_HOSTS = [
    'django-lessons.test', '*'
]
INTERNAL_IPS = ('127.0.0.1',)
STATIC_ROOT = '/opt/django-lessons/static'

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.StreamHandler',
        },
    },
    'formatters': {
        'with_funcname': {
            'format': '[{pathname}:{funcName}:{lineno:d}] {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'lessons': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}


AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_S3_CUSTOM_DOMAIN = os.environ['AWS_S3_CUSTOM_DOMAIN']

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
THUMBNAIL_DEFAULT_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

EMAIL_FROM = 'eugen@django-lessons.com'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/home/eugen/django_emails/'


# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': os.environ['GITHUB_CLIENT_ID'],
            'secret': os.environ['GITHUB_SECRET'],
            'key': os.environ['GITHUB_KEY']
        }
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.environ['GOOGLE_CLIENT_ID'],
            'secret': os.environ['GOOGLE_SECRET'],
        }
    }
}

STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
STRIPE_PLAN_MONTHLY_ID = os.environ['STRIPE_PLAN_MONTHLY_ID']
STRIPE_PLAN_ANNUAL_ID = os.environ['STRIPE_PLAN_ANNUAL_ID']
STRIPE_WEBHOOK_SIGNING_KEY = os.environ['STRIPE_WEBHOOK_SIGNING_KEY']


PAYPAL_PLAN_MONTHLY_ID = os.environ.get('PAYPAL_PLAN_MONTHLY_ID')
PAYPAL_PLAN_ANNUAL_ID = os.environ.get('PAYPAL_PLAN_ANNUAL_ID')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID')

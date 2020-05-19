import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@8=$y!gnmw16e6vbk#i%s=oqis4zii5xzr&uv9=u#-kt%7je0a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
STATIC_ASSETS_VER = None

# Application definition

INSTALLED_APPS = [
    'lessons',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.modeladmin',
    'taggit',
    'django_extensions',
    'storages',
    'easy_thumbnails',
    'django.contrib.admin',
    # sites, auth, messages are required by allauth
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google'
]

MIDDLEWARE = [
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'lessons.context_processors.courses'
            ],
        },
    },
]


AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

WAGTAIL_SITE_NAME = 'Django Lessons Site'
SITE_ID = 1


# allauth
ACCOUNT_EMAIL_REQUIRED = True
LOGIN_REDIRECT_URL = '/'
# user needs to confirm his/her email before logging in
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'


WEBSITE = "django-lessons.com"
SERVICE_NAME = "Django Lessons"
SERVICE_EMAIL = "eugen@django-lessons.com"


# /home/eugen/projects/Django-Lessons.py/.venv/lib/python3.8/site-packages/storages/backends/s3boto3.py:340:
# /UserWarning: The default behavior of S3Boto3Storage is insecure and will
# /change in django-storages 1.10. By default files and new buckets are saved
# /with an ACL of 'public-read' (globally publicly readable). Version 1.10
# /will default to using the bucket's ACL. To opt into the new behavior set
# /AWS_DEFAULT_ACL = None, otherwise to silence this warning explicitly set
# /AWS_DEFAULT_ACL.
# AWS_DEFAULT_ACL = None
from django.contrib.messages import constants as messages  # noqa

MESSAGE_TAGS = {
    messages.INFO: 'text-primary',
    messages.SUCCESS: 'text-success',
    messages.WARNING: 'text-warning',
    messages.ERROR: 'text-danger'
}


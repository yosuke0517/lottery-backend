from .base import *
import os

DEBUG = True

INSTALLED_APPS += [
    'django_extensions',
]

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lotterydb',
        'USER': 'lottery',
        'PASSWORD': 'lottery',
        'HOST': 'db',
        'PORT': 5432
    }
}

STATIC_URL = '/static/'

STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))
from .base import *
import environ

env = environ.Env()
env.read_env('.env')

DEBUG = False

INSTALLED_APPS += [
    'gunicorn',
]

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_NAME'),
        'USER': env('USER_NAME'),
        'PASSWORD': env('PASSWORD'),
        'HOST': env('HOST'),
        'PORT': 5432
    }
}

CORS_ORIGIN_WHITELIST = [
    'https://2021lottery.tk',
    '18.177.145.215'
]

STATIC_URL = '/static/'

STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))
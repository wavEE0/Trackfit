"""
Django settings for trackfit project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-orb7vi*nla_2-w(3zzyze=%%&90^4)0_94!vge7qxn9e&+648&')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

_extra_hosts = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + _extra_hosts

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'crispy_forms',
    'nutrition',
    'trackfit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trackfit.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]}}]

WSGI_APPLICATION = 'trackfit.wsgi.application'

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME':     os.environ.get('DB_NAME',     'trackfit'),
    'USER':     os.environ.get('DB_USER',     'db_user'),
    'PASSWORD': os.environ.get('DB_PASSWORD', 'awda'),
    'HOST':     os.environ.get('DB_HOST',     'localhost'),
    'PORT':     os.environ.get('DB_PORT',     '5432'),
}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CLIENT_ID     = os.environ.get('AUTH0_CLIENT_ID',     'BCr82WYN7uLkc7Evgz5NpZqc3LtE6P3P')
AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET', 'yGiZi36KsNY0BTJI-twq1ocUZO5Ko8JIdvs7cMr3wGd-UJrlcsUJ9qMp5Lh9KCuz')
AUTH0_DOMAIN        = os.environ.get('AUTH0_DOMAIN',        'dev-cwb7tl31pjlauvtc.us.auth0.com')

AUTH_USER_MODEL = 'trackfit.User'
CRISPY_TEMPLATE_PACK = 'bootstrap4.3.1'

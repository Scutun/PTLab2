"""
Django settings for tplab2 project.

Настройки читаются из переменных окружения, поэтому один и тот же код
работает локально, в GitHub Actions и на хостинге Render:

* DATABASE_URL       – строка подключения к БД (Render/Neon, GitHub Actions);
                       если не задана, используется локальный PostgreSQL
                       (база django_db, пароль из DATABASE_PASSWORD);
* SECRET_KEY         – секретный ключ Django (на хостинге обязателен);
* DJANGO_DEBUG       – "True"/"False"; по умолчанию True локально и False
                       на Render (там задана переменная RENDER);
* RENDER_EXTERNAL_HOSTNAME – доменное имя сервиса, Render задаёт его сам.
"""

import os
import warnings
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-%hodks^u@arq^bv-tms#o!v$c*p6_5o%yvw!!u+n9ber@*g9*f',
)

DEBUG = os.environ.get(
    'DJANGO_DEBUG', 'False' if 'RENDER' in os.environ else 'True'
) == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']
    # Render принимает HTTPS и передаёт запрос приложению по HTTP
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'shop.apps.ShopConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'tplab2.urls'

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
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tplab2.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', '')
DATABASES = {
    'default': dj_database_url.config(
        default=(f'postgres://postgres:{DATABASE_PASSWORD}'
                 f'@localhost:5432/django_db'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Volgograd'

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# Папка staticfiles создаётся командой collectstatic только при
# развёртывании; локально и в тестах предупреждение WhiteNoise не нужно.
warnings.filterwarnings('ignore', message='No directory at')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

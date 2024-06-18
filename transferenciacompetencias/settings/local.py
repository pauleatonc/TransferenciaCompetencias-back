from .base import *
import environ
import os

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

API_PATH_PREFIX = env("API_PATH_PREFIX", default="")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    # Base de datos de aplicación
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_DEFAULT_NAME'),
        'USER': env('DATABASE_DEFAULT_USER'),
        'PASSWORD':env('DATABASE_DEFAULT_PASSWORD'),
        'HOST': env('DATABASE_DEFAULT_HOST'),
        'PORT': env('DATABASE_DEFAULT_PORT'),
    },
                }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR.child('static')]
STATIC_ROOT = BASE_DIR.child('staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')

# EMAIL SETTINGS
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587

# RECAPTCHA SETTINGS
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')

# SENDGRID SETTINGS
SENDGRID_API_KEY = env('SENDGRID_API_KEY')
ADMIN_EMAIL = env("ADMIN_EMAIL")
NOREPLY_EMAIL = env("NOREPLY_EMAIL")

# KEYCLOAK SETTINGS
KEYCLOAK_CONFIG = {
    'realm': env('LOCAL_KEYCLOAK_REALM'),
    'auth-server-url': env('LOCAL_KEYCLOAK_AUTH_SERVER_URL'),
    'ssl-required': env('LOCAL_KEYCLOAK_SSL_REQUIRED'),
    'resource': env('LOCAL_KEYCLOAK_RESOURCE'),
    'credentials': {
        'secret': env('LOCAL_KEYCLOAK_CREDENTIALS_SECRET')
    },
    'confidential-port': env.int('LOCAL_KEYCLOAK_CONFIDENTIAL_PORT'),
    'redirect_uri': env('LOCAL_KEYCLOAK_REDIRECT_URI'),
    'keycloak_token_url': env('LOCAL_KEYCLOAK_TOKEN_URL'),
    'keycloak_logout_url': env('LOCAL_KEYCLOAK_LOGOUT_URL'),
}


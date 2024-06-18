import environ
import os
from .base import *

# we load the variables from the .env file to the environment
env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
# Your secret key
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = [ 'qatc.subdere.gob.cl', ]

API_PATH_PREFIX = env("API_PATH_PREFIX", default="")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    # Base de datos de aplicación
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': 'Transferenciadb',
        'PORT': env("DB_PORT"),
    }
        # Base de datos externa
        # Revisar cómo setiaremos la base de datos externa en ambiente de desarrollo. Para poder testear la importación de usuarios.

}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles', 'transferenciacompetencias')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")

# Sendgrid
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
ADMIN_EMAIL = env("ADMIN_EMAIL")
NOREPLY_EMAIL = env("NOREPLY_EMAIL")

# KEYCLOAK SETTINGS
KEYCLOAK_CONFIG = {
    'realm': env('DEV_KEYCLOAK_REALM'),
    'auth-server-url': env('DEV_KEYCLOAK_AUTH_SERVER_URL'),
    'ssl-required': env('DEV_KEYCLOAK_SSL_REQUIRED'),
    'resource': env('DEV_KEYCLOAK_RESOURCE'),
    'credentials': {
        'secret': env('DEV_KEYCLOAK_CREDENTIALS_SECRET')
    },
    'confidential-port': env.int('DEV_KEYCLOAK_CONFIDENTIAL_PORT'),
    'redirect_uri': env('DEV_KEYCLOAK_REDIRECT_URI'),
    'keycloak_token_url': env('DEV_KEYCLOAK_TOKEN_URL'),
    'keycloak_logout_url': env('DEV_KEYCLOAK_LOGOUT_URL'),
}

# Trusted origins for the CSRF validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# If we are behind proxy with https we trust the header defined here.
# https://docs.djangoproject.com/en/4.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = env.tuple('SECURE_PROXY_SSL_HEADER', default=None)

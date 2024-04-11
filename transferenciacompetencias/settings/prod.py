import environ
import os
from .base import *

# we load the variables from the .env file to the environment
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
# Your secret key
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

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
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
    }
        # Base de datos externa
        # Revisar cómo setiaremos la base de datos externa en ambiente de desarrollo. Para poder testear la importación de usuarios.

}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'staticfiles/'
STATICFILES_DIRS = [BASE_DIR.child('static')]

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILES_LOCATION = 'media'

# Bucket Storage Configuration
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")  # e.g. us-west-2
AWS_S3_FILE_OVERWRITE = env.bool('AWS_S3_FILE_OVERWRITE', default=False)
AWS_DEFAULT_ACL = None


RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")

# Sendgrid
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
ADMIN_EMAIL = env("ADMIN_EMAIL")
NOREPLY_EMAIL = env("NOREPLY_EMAIL")


# Trusted origins for the CSRF validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# If we are behind proxy with https we trust the header defined here.
# https://docs.djangoproject.com/en/4.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = env.tuple('SECURE_PROXY_SSL_HEADER', default=None)

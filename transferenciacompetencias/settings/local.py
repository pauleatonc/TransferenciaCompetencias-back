from .base import *
import environ
import os

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-d!nd%p#gxqzw2qs1&9&!fd(v4hr@^^0ls*uh!4-kiv^a)&5c^%'

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
        'NAME': 'Transferenciadb',
        'USER': 'postgres',
        'PASSWORD':'Subdere.2022',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    # Base de datos externa
    'externaldb': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'externaldb',
        'USER': 'postgres',
        'PASSWORD': 'Subdere.2022',
        'HOST': 'localhost',
        'PORT': '5432',
            }
                }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.child('static')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')

# EMAIL SETTINGS
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'modernizacion@subdere.gov.cl'
EMAIL_HOST_PASSWORD = 'Subde*moder23'
EMAIL_PORT = 587

# RECAPTCHA SETTINGS
RECAPTCHA_PUBLIC_KEY = '6LemsJgmAAAAAJj8noe-1FWZgl0ltkX5SeGgBa0h'
RECAPTCHA_PRIVATE_KEY = '6LemsJgmAAAAAG8rwzcmMJVPx1t8VLpT86vWju-i'

# SENDGRID SETTINGS
SENDGRID_API_KEY = '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'
ADMIN_EMAIL = ['modernizacion@subdere.gov.cl']
NOREPLY_EMAIL = ['noreply@bancoproyectos.subdere.gob.cl']


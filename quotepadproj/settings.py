"""
Django settings for quotepadproj project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'imw6@yb#gl*)_ma3jfkz8%0ie3ql8t7y+9j9splpwnm@@rhsue'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.0.42','localhost','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'quotepad',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'formtools',
    'payments.apps.PaymentsConfig',
    'import_export',
    'django.contrib.humanize',
    #'rest_framework',
    #'Rest',
    #'corsheaders'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quotepadproj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'quotepad.context_processors.static_vars',
            ],
        },
    },
]

WSGI_APPLICATION = 'quotepadproj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'en-GB'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_INPUT_FORMATS = ['%d-%m-%Y']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

LOGIN_REDIRECT_URL = '/loginredirect/'
LOGOUT_REDIRECT_URL = '/landing/'

# - Location setting for the files being uploaded
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Settings for send emails to mailtrap.io
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_USER = '81fe8f4f745013'
EMAIL_HOST_PASSWORD = '42e4ef999c2411'
EMAIL_PORT = '2525'

# Stripe key settings
STRIPE_SECRET_KEY = 'sk_test_4YVK8BcxtDC2f0F7DVau0JWG00TJj1bFLs'
STRIPE_PUBLISHABLE_KEY = 'pk_test_34Pl9iMCAFEIfxCGX84ZrP6G0047uZg93B'

# yourheat master settings
YH_MASTER_PROFILE_ID = 6
YH_MASTER_PROFILE_USERNAME = 'yourheatx'
YH_TEST_EMAIL = True
YH_URL_STATIC_FOLDER = 'http://127.0.0.1:8000/static/'    # Set this to the static folder on the live server

# SmartSheet integration settings for test Smartsheet
#YH_SS_PRODUCTION_SITE = False
#YH_SS_INTEGRATION = True
#YH_SS_ACCESS_TOKEN = 'rix4kc3qoulzw42y4ukuqyfxfe'
#YH_SS_SHEET_NAME = "Master Database"
#YH_SS_SURVEY_REPORT = "20.0 All Booked Surveys"
#YH_SS_TRACK_COMMS_SENT = False

# SmartSheet integration settings for live Smartsheet
YH_SS_PRODUCTION_SITE = False       # Setting to determine whether a proxy server needs to be access ( only for PythonAnyhwere )
YH_SS_INTEGRATION = False
#YH_SS_ACCESS_TOKEN = '727cjzxr1715oenualfctjcsoi'
YH_SS_ACCESS_TOKEN = '2JvwbHDONLyZ7f7juDEEdV4b4WlUuXMHGioGr'
YH_SS_SHEET_NAME = "Master Database Boiler"
YH_SS_SURVEY_REPORT = "Customers for Survey to QP"
YH_SS_TRACK_COMMS_SENT = False      # Flag to determine if the Customer Comm model is updated
YH_QUOTE_ACCEPTED_EMAILS = ['tom.hewitt@yourheat.co.uk,tom.driscoll@yourheat.co.uk,jeremy.tomkinson@yourheat.co.uk']

# Google Calendar settings
YH_CAL_ENABLED = True

# REST Framework Authentication settings

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' : ('rest_framework.permissions.IsAuthenticatedOrReadOnly',)
}

CORS_ORIGIN_ALLOW_ALL = True

# XERO Integration Settings
# GL Account Settings
#YH_XERO_CLIENT_ID = '9407B59E6ACE4DA8A3B1F83B6CB5969D'
#YH_XERO_CLIENT_SECRET = 'HvfRYoLVhovXhHG754aPY2tjk-5Mw8YxE0jwJLAZVqttJ9d1'
#YH_XERO_REDIRECT_URL = 'http://localhost:8000/XeroRedirect/'
#YH_XERO_SCOPE = 'offline_access accounting.transactions accounting.contacts'

#YH Account settings
YH_XERO_CLIENT_ID = 'F29F53F0BF5E41098A2B0764C4F4B2D1'
YH_XERO_CLIENT_SECRET = 'XpagSGc0Jkri2u7acPCOkdCsw37nzu_mJAudKM1PwnV48kwb'
YH_XERO_REDIRECT_URL = 'http://localhost:8000/XeroRedirect/'
YH_XERO_SCOPE = 'offline_access accounting.transactions accounting.contacts'

# Invoice Settings
DEPOSIT_INVOICE_DESCRIPTION = "Deposit amount due for Boiler Installation and associated works."
BALANCE_INVOICE_DESCRIPTION = "Balance due for completion of Boiler Installation and associated works."
DEPOSIT_RECEIPT_DESCRIPTION = "Deposit Payment for Boiler Installation and associated works."
BALANCE_RECEIPT_DESCRIPTION = "Balance Payment for Boiler Installation and associated works."



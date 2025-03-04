"""
Django settings for pri project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import yaml
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dummy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    # 'django.forms',

    'rest_framework',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'two_factor.plugins.phonenumber',
    'encrypted_fields',
    'prettyjson',
    'localflavor',
    'phonenumber_field',
    'precise_bbcode',

    'users',
    'fleet',
    'sales',
    'service',
    'consignment',
    'marketing',
    'content',
    'customer_portal',
    'backoffice',
    'legacy',

    # Wagtail
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    "wagtail.contrib.table_block",
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'modelcluster',
    'taggit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'pri.middleware.LoginRequiredMiddleware',
    'pri.middleware.PermissionsMiddleware',
    'pri.middleware.RemoteHostMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'pri.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pri.context_processors.settings_constants',
            ],
        },
    },
]
# FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'pri.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'front': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_front.sqlite3',
    },
    'default_legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'PRIB',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': None,
        'PASSWORD': None,
        'OPTIONS': {
            'init_command': 'SET character_set_connection=utf8mb4, collation_connection=utf8mb4_general_ci',
            'charset': 'utf8mb4',
        },
    },
    'front_legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'PRIF',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': None,
        'PASSWORD': None,
        'OPTIONS': {
            'init_command': 'SET character_set_connection=utf8mb4, collation_connection=utf8mb4_general_ci',
            'charset': 'utf8mb4',
        },
    },
}

DATABASE_ROUTERS = ('pri.db_routers.FrontDBRouter',)


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.User'

AUTH_EXEMPT_ROUTES = (
    'login',
    'password_reset',
    'password_reset_confirm',
)

# This logging setup has the following attributes:
# When DEBUG = True, debug information will be displayed on requested page.
# It will also show any errors/warnings/info in the console output.
# When DEBUG = False (on production), no debug information will be displayed
# but any errors will be logged in /logs/django.log (project_dir)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'datefmt': '%d/%b/%Y %H:%M:%S',
            'format': '%(purple)s[%(asctime)s] %(cyan)s[%(name)s:%(lineno)s] %(log_color)s%(levelname)-4s%(reset)s %(white)s%(message)s',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'logfile': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(BASE_DIR) + '/logs/django.log',
            'maxBytes': 1024 * 1024 * 64,  # 64mb
            'backupCount': 5,
            'formatter': 'colored',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'WARN',
            'handlers': ['logfile'],
        }
    },
}

LOGIN_URL = 'two_factor:login'
# LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/two_factor/'

LOG_AUTH = False

REST_FRAMEWORK = {
   'DEFAULT_AUTHENTICATION_CLASSES': (
       # 'rest_framework.authentication.BasicAuthentication',
       # 'rest_framework.authentication.SessionAuthentication',
   )
}


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SITE_ID = 1


# TEST_RUNNER = 'pri.test_runner.PytestTestRunner'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'site_media')
MEDIA_URL = '/media/'

SERVER_BASE_URL = 'https://performance.rentals'

ADMINS = [('Brian Tiemann', 'btman@mac.com')]

ADMIN_ENABLED = False

COMPANY_NAME = 'Performance Rentals'
COMPANY_PHONE = '(866) 607-0084'
COMPANY_FAX = '(845) 357-3535'
# COMPANY_ADDRESS = '373 Margaret King Ave, Ringwood NJ 07430'
COMPANY_ADDRESS = '''
5701 Lawton Dr
Sarasota FL 34233
'''
COMPANY_CITY_FOR_DELIVERY = 'Sarasota, FL'  # "Ringwood, NJ"
COMPANY_FOUNDING_YEAR = 2008
SUPPORT_EMAIL = 'support@performance.rentals'
SITE_EMAIL = 'info@performancerentals.us'
DEBUG_EMAIL = 'btman@mac.com'
RESERVATIONS_EMAIL = 'reservations@performancerentals.us'
SALES_EMAIL = 'sales@performancerentals.us'
DEFAULT_FROM_EMAIL = SITE_EMAIL

WAGTAIL_SITE_NAME = 'Performance Rentals'
WAGTAILADMIN_BASE_URL = 'http://127.0.0.1:8000/cms'

os.environ['WKHTMLTOPDF_BIN'] = '/usr/local/bin/wkhtmltopdf'

# Choices for country picker for vehicle origins
COUNTRIES_ONLY = ['US', 'JP', 'IT', 'GB', 'DE', 'AT']

PHONENUMBER_DEFAULT_REGION = 'US'

PIC_MAX_WIDTH = 1000
PIC_MAX_HEIGHT = 1000
THUMB_MAX_WIDTH = 150
THUMB_MAX_HEIGHT = 150

EXTRA_MILES_PRICES = {
    0: {'value': 0, 'label': 'None', 'cost': 0},
    100: {'value': 100, 'label': '100 miles ($175)', 'cost': 175},
    150: {'value': 150, 'label': '150 miles ($255)', 'cost': 255},
    200: {'value': 200, 'label': '200 miles ($330)', 'cost': 330},
    250: {'value': 250, 'label': '250 miles ($400)', 'cost': 400},
}
EXTRA_MILES_OVERAGE_PER_MILE = 1.95

JOY_RIDE_PRICES = {
    '1_pax': 250,
    '2_pax': 450,
    '3_pax': 675,
    '4_pax': 900,
    'cost_per_pax_gt_4': 200
}

PERFORMANCE_EXPERIENCE_PRICES = {
    '1_drv': 450,
    '2_drv': 800,
    '3_drv': 1100,
    '4_drv': 1300,
    'cost_per_drv_gt_4': 300,
    'cost_per_pax': 75
}

MILITARY_DISCOUNT_PCT = 10
SURVEY_DISCOUNT_PCT = 5

EXTEND_THRESHOLD_HOURS = 6
# 30m + 1 second to allow reservations of up to 30m beyond the time of delivery
RENTAL_GRACE_PERIOD_SECS = 1801

# Backoffice site seconds of idle until push to "sleeping" page
ADMIN_SLEEP_TIMEOUT_SECS = 1500

FIELD_ENCRYPTION_KEYS = None

MOBILE_KEY = None

# Sales tax calculation API
AVALARA_ACCOUNT_ID = None
AVALARA_API_KEY = None
AVALARA_APP_NAME = 'Performance Rentals, Inc.'
AVALARA_APP_VERSION = 'v0.1'
AVALARA_MACHINE_NAME = 'Backend server 001'
AVALARA_ENVIRONMENT = None
DEFAULT_TAX_ZIP = '07456'
DEFAULT_TAX_RATE = '0.07'

# Stripe
STRIPE_ENABLED = True
STRIPE_CUSTOMER_ENABLED = True
STRIPE_PUBLIC_KEY = None
STRIPE_SECRET_KEY = None
CARD_NUMBER_OVERRIDE = None

COLLECT_CARD_INFO = True

# Twitter
TWITTER_ENABLED = True

# Google Maps embed API
GOOGLE_MAPS_API_KEY = None

# For migrating from legacy
LEGACY_SITE_ROOT = 'http://performancerentals.us/'
LEGACY_SITE_SEC_ROOT = 'https://secure.performancerentals.us/'
LEGACY_GLOBAL_KEY = None

# TinyMCE API key
TINYMCE_API_KEY = None

TITLE_BAR_LINE_1 = 'Sports car rentals for the automotive enthusiast'
TITLE_BAR_LINE_2 = 'Serving the NYC area and beyond'

# ReCAPTCHA settings & keys
RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = None
RECAPTCHA_SECRET_KEY = None
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

# Show the bike fleet?
BIKES_ENABLED = True

# Date and time representation formats in form fields
DATE_FORMAT_INPUT = '%m/%d/%Y'
TIME_FORMAT_INPUT = '%H:%M'

# Anti-abuse settings

# Set to True to block all reservation creation and send all requests (i.e. by a bot) to a honeypot result page
KILL_SWITCH = False
# If more than COUNT customers are registered from the same IP within INTERVAL_MINS minutes, create an IPBan
REGISTRATION_FROM_SAME_IP_AUTO_BLOCK = True
REGISTRATION_FROM_SAME_IP_COUNT = 2
REGISTRATION_FROM_SAME_IP_INTERVAL_MINS = 10


# Local overrides from env.yaml
with open(os.path.join(BASE_DIR, 'env.yaml')) as f:
    local_settings = yaml.load(f, Loader=yaml.FullLoader)
globals().update(local_settings)

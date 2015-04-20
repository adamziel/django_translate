
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Customize django settings:

DEBUG = True

INSTALLED_APPS = (
    # Since this module are imported, DebugTranslator will complain about
    # lack of translations if we don't include it in INSTALLED_APPS or
    # TRANZ_LOCALE_PATHS. We can of course use the default translator
    # class and not worry about it
    'django.contrib.contenttypes',
    'django.contrib.auth.models', 
    
    'django_translate',
    
    'example_dropin.translate'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.locale.LocaleMiddleware',
    'django_translate.middleware.LocaleMiddleware',    
)

SECRET_KEY = 'not_so_secret'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'english'),
    ('fr', 'french'),
)
    
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Adjust django_translate settings:

# Set this to False to use django translations again
TRANZ_REPLACE_DJANGO_TRANSLATIONS = True


# In DEBUG we want to use DebugTranslator - it reloads
# your translations on-the-fly so it's very easy to work with them
# It will also throw an exception whenever there is any problem
# with your translations (e.g. a translation is not found) - no more
# guessing "why my translations are not used?"
if DEBUG:
    from python_translate.translations import DebugTranslator
    TRANZ_TRANSLATOR_CLASS = DebugTranslator

# You do not need to alter TRANZ_LOADERS as in example_basic,
# because setting TRANZ_REPLACE_DJANGO_TRANSLATIONS to True
# will add appropriate loader for *.po files for you (unless
# one is explicitly provided in here)



# All settings below are the default ones:


ALLOWED_HOSTS = []

ROOT_URLCONF = 'example_dropin.urls'

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

WSGI_APPLICATION = 'example_dropin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

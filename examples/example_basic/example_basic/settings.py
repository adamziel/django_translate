
# Customize django settings:

DEBUG = True

INSTALLED_APPS = (
    'django_translate',
    'example_basic.translate'
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
    
# Adjust django_translate settings:

# In DEBUG we want to use DebugTranslator - it reloads
# your translations on-the-fly so it's very easy to work with them
# It will also throw an exception whenever there is any problem
# with your translations (e.g. a translation is not found) - no more
# guessing "why my translations are not used?"
if DEBUG:
    from python_translate.translations import DebugTranslator
    TRANZ_TRANSLATOR_CLASS = DebugTranslator


# By default only "json" and "yml" loaders are enabled,
# but we want to use "po" files in this example
from python_translate import loaders
TRANZ_LOADERS = {
    "po": loaders.PoFileLoader(),
    "yml": loaders.YamlFileLoader()
}

# All settings below are the default ones:

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


ALLOWED_HOSTS = []

ROOT_URLCONF = 'example_basic.urls'

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

WSGI_APPLICATION = 'example_basic.wsgi.application'


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

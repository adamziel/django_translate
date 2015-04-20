# -*- coding: utf-8 -*-
import os
from django.conf import settings
import python_translate.extractors as extractors
import python_translate.extractors.base
import python_translate.extractors.python
import django_translate.extractors.django_template

import python_translate.dumpers as dumpers

from python_translate import loaders
from python_translate import translations
from python_translate import glue

def _d(param, default_value):
    if hasattr(settings, param):
        return getattr(settings, param)
    else:
        return default_value()
    
TRANZ_LANGUAGES = _d('TRANZ_LANGUAGES', lambda: _d('LANGUAGES', []))

TRANZ_EXCLUDED_DIRS = _d('TRANZ_EXCLUDED_DIRS', lambda: [])
TRANZ_EXCLUDED_DIRS.append(os.path.dirname(os.path.abspath(__file__)))

TRANZ_LOADERS = _d('TRANZ_LOADERS', lambda: {
    "json": loaders.JSONFileLoader(),
    "yml": loaders.YamlFileLoader()
})

TRANZ_DUMPERS = _d('TRANZ_DUMPERS', lambda: {
    "json": dumpers.JSONFileDumper(),
})

TRANZ_EXTRACTORS = _d('TRANZ_EXTRACTORS', lambda: {
    "template": django_translate.extractors.django_template.DjangoTemplateExtractor(),
    "py": extractors.python.PythonExtractor()
})

TRANZ_LOADER_CLASS = _d('TRANZ_LOADER_CLASS', lambda: glue.TransationLoader)
TRANZ_WRITER_CLASS = _d('TRANZ_WRITER_CLASS', lambda: glue.TranslationWriter)

TRANZ_EXTRACTOR_CLASS = _d('TRANZ_EXTRACTOR_CLASS',
                            lambda: extractors.base.ChainExtractor)

TRANZ_TRANSLATOR_CLASS = _d('TRANZ_TRANSLATOR_CLASS',
                             lambda: translations.Translator)

TRANZ_REPLACE_DJANGO_TRANSLATIONS = _d('TRANZ_REPLACE_DJANGO_TRANSLATIONS', lambda: False)

TRANZ_SEARCH_LOCALE_IN_APPS = _d('TRANZ_SEARCH_LOCALE_IN_APPS', lambda: True)
TRANZ_DIR_NAME = _d('TRANZ_DIR_NAME', lambda: 'tranz')

TRANZ_LOCALE_PATHS = _d('TRANZ_LOCALE_PATHS', lambda: [])

if not isinstance(TRANZ_LOCALE_PATHS, (tuple, list)):
    raise ValueError("TRANZ_LOCALE_PATHS must be a tuple or a list")

TRANZ_DEFAULT_LANGUAGE = _d('TRANZ_DEFAULT_LANGUAGE', lambda: "en")

if TRANZ_REPLACE_DJANGO_TRANSLATIONS:
    TRANZ_LOCALE_PATHS = list(TRANZ_LOCALE_PATHS) + list(_d('LOCALE_PATHS', lambda: []))
    
    # Ugly hack to make sure Django-provided translations are loaded too
    import django
    TRANZ_LOCALE_PATHS += [os.path.join(os.path.dirname(django.__file__), 'conf', 'locale')]
    
    if "mo" not in TRANZ_LOADERS:
        TRANZ_LOADERS["mo"] = loaders.DummyLoader() # We want to ignore .mo files
        
    if "po" not in TRANZ_LOADERS:
        TRANZ_LOADERS["po"] = loaders.PoFileLoader()


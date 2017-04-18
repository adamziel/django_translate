# -*- coding: utf-8 -*-
"""
Do not import before django is initialized or you will run into
circular imports
"""

import os
from collections import defaultdict

from django.apps.registry import apps
from python_translate import loaders
from python_translate import translations

from django_translate import settings


def discover_resources():
    """
    Searches for translations files matching [catalog].[lang].[format]

    Traverses TRANZ_LOCALE_PATHS:
    -
    | TRANZ_LOCALE_PATHS
     +- messages.fr.yml
      | messages.en.yml

    And apps paths if TRANZ_SEARCH_LOCALE_IN_APPS is set to True):
    -
    | app_path
    +- TRANZ_DIR_NAME
     +- messages.fr.yml
      | messages.en.yml

    @rtype: list
    @return: A list of all found translation files
    """
    locale_discovery_paths = list(settings.TRANZ_LOCALE_PATHS)
    if settings.TRANZ_SEARCH_LOCALE_IN_APPS:
        locale_discovery_paths += [os.path.join(app.path, settings.TRANZ_DIR_NAME) for app in list(apps.app_configs.values())]
        
    APP_LANGUAGES = [l[0] for l in settings.TRANZ_LANGUAGES]

    resources = []
    for path in locale_discovery_paths:
        if not os.path.isdir(path):
            continue

        # Try to match direct children or discovery paths
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                try:
                    domain, lang, format = file.split('.')
                except ValueError as e:
                    continue
                resources.append((format, os.path.join(path, file), lang, domain))
        
        
        # Try to match django's LC_MESSAGES directories
        if settings.TRANZ_REPLACE_DJANGO_TRANSLATIONS:
            for lang in APP_LANGUAGES:
                if os.path.isdir(os.path.join(path, lang)):
                    LC_MESSAGES_PATH = os.path.join(path, lang, 'LC_MESSAGES')
                    if os.path.isdir(LC_MESSAGES_PATH):
                        for file in os.listdir(LC_MESSAGES_PATH):
                            try:
                                domain, format = file.split('.')
                            except ValueError as e:
                                continue
                            resources.append((format, os.path.join(LC_MESSAGES_PATH, file), lang, domain))
    return resources


translator = settings.TRANZ_TRANSLATOR_CLASS(settings.TRANZ_DEFAULT_LANGUAGE)
for format, loader in list(settings.TRANZ_LOADERS.items()):
    translator.add_loader(format, loader)

for format, path, locale, domain in discover_resources():
    translator.add_resource(format, path, locale, domain)

_ = translator.trans
trans = tranz = translator.trans
transchoice = tranzchoice = translator.transchoice

loader = settings.TRANZ_LOADER_CLASS()
for format, subloader in list(settings.TRANZ_LOADERS.items()):
    loader.add_loader(format, subloader)

writer = settings.TRANZ_WRITER_CLASS()
for format, subdumper in list(settings.TRANZ_DUMPERS.items()):
    writer.add_dumper(format, subdumper)

extractor = settings.TRANZ_EXTRACTOR_CLASS()
for format, subextractor in list(settings.TRANZ_EXTRACTORS.items()):
    extractor.add_extractor(format, subextractor)

def monkeypatch_django():
    from django.utils import translation
    from django.utils.translation import trans_real
    
    def get_locale():
        if trans_real._active and hasattr(trans_real._active, "value"):
            return trans_real._active.value.language()
        
        if trans_real._default and hasattr(trans_real._default, "_DjangoTranslation__locale"):
            return trans_real._default._DjangoTranslation__locale
        
        return settings.TRANZ_DEFAULT_LANGUAGE
    
    def gettext_patch(message):
        return trans(message, domain='django', locale=get_locale())
    
    def contextual_gettext_patch(context, message):
        return gettext_patch(message)
        
    def plural_gettext_patch(singular, plural, n):
        return transchoice(plural, n, domain='django', locale=get_locale())

    def contextual_plural_gettext_patch(context, singular, plural, n):
        return plural_gettext_patch(singular, plural, n)
    
    setattr(translation, "gettext", gettext_patch)
    setattr(translation, "ngettext", gettext_patch)
    setattr(translation, "ugettext", gettext_patch)
    setattr(translation, "gettext_lazy", gettext_patch)
    setattr(translation, "ugettext_lazy", gettext_patch)
    
    setattr(translation, "pgettext", contextual_gettext_patch)
    setattr(translation, "pgettext_lazy", contextual_gettext_patch)
    
    setattr(translation, "ngettext", plural_gettext_patch)
    setattr(translation, "ungettext", plural_gettext_patch)
    setattr(translation, "ngettext_lazy", plural_gettext_patch)
    setattr(translation, "ungettext_lazy", plural_gettext_patch)
    setattr(translation, "do_ntranslate", lambda _1, _2, _3, _4: plural_gettext_patch(_1, _2, _3))
    
    setattr(translation, "npgettext", contextual_plural_gettext_patch)
    setattr(translation, "npgettext_lazy", contextual_plural_gettext_patch)
    
    from django.template import base as base_template
    setattr(base_template, "ugettext_lazy", gettext_patch)
    setattr(base_template, "pgettext_lazy", contextual_gettext_patch)
    
    from django.template import defaultfilters
    setattr(defaultfilters, "ugettext", gettext_patch)
    setattr(defaultfilters, "ungettext", plural_gettext_patch)
    


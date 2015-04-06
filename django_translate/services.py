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
    locale_discovery_paths = settings.TRANZ_LOCALE_PATHS
    if settings.TRANZ_SEARCH_LOCALE_IN_APPS:
        locale_discovery_paths += [os.path.join(app.path, '/', settings.TRANZ_DIR_NAME ) for app in apps.app_configs.values()]

    resources = []
    for path in locale_discovery_paths:
        if not os.path.isdir(path):
            continue

        ls = os.listdir(path)

        # Try to match direct children or discovery paths
        for file in ls:
            if os.path.isfile(os.path.join(path, file)):
                try:
                    domain, lang, format = file.split('.')
                except ValueError as e:
                    continue
                resources.append((format, os.path.join(path, file), lang, domain))
    return resources


translator = settings.TRANZ_TRANSLATOR_CLASS(settings.TRANZ_DEFAULT_LANGUAGE)
for format, loader in settings.TRANZ_LOADERS.items():
    translator.add_loader(format, loader)

for format, path, locale, domain in discover_resources():
    translator.add_resource(format, path, locale, domain)

_ = translator.trans
trans = translator.trans
transchoice = translator.transchoice

loader = settings.TRANZ_LOADER_CLASS()
for format, subloader in settings.TRANZ_LOADERS.items():
    loader.add_loader(format, subloader)

writer = settings.TRANZ_WRITER_CLASS()
for format, subdumper in settings.TRANZ_DUMPERS.items():
    writer.add_dumper(format, subdumper)

extractor = settings.TRANZ_EXTRACTOR_CLASS()
for format, subextractor in settings.TRANZ_EXTRACTORS.items():
    extractor.add_extractor(format, subextractor)

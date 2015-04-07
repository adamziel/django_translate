# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import os.path
import re
import sys
import string

from django.apps.registry import apps
from django.core.management.base import BaseCommand, CommandError
from python_translate.extractors import base as extractors
from python_translate import operations
from python_translate.translations import MessageCatalogue

import django_translate
from django_translate.utils import bcolors
from django_translate import services
from django_translate import settings


class AnyFormatSpec:

    def __format__(self, fmt):
        return ''


class Formatter(string.Formatter):

    def __init__(self):
        self.used = set()

    def get_value(self, key, args, kwargs):
        self.used.add(key)
        return AnyFormatSpec()


class Command(BaseCommand):

    help = """Validates translation strings from templates from a given location.

              Example running against app folder
                  ./manage.py tranzvalidate -l en --app website
                  ./manage.py tranzvalidate -l fr --path ./ --tranz-dir ./tranz --exclude ./static
              """

    def __init__(self, stdout=None, stderr=None, no_color=False):
        self.excluded_paths = None
        self.locale = None
        self.verbosity = None

        super(Command, self).__init__(stdout, stderr, no_color)


    def add_arguments(self, parser):
        parser.add_argument('--locale', '-l', default='en', dest='locale', action='store',
                            help='Locale to process')

        parser.add_argument('--app', '-a', dest='app', action='store',
                            help='App to scan.')

        parser.add_argument('--path', '-p', dest='path', action='store',
                            help='Path to scan')

        parser.add_argument('--tranz-dir', dest='tranz_dir', default=None, action='store',
                            help='Override the default tranz dir (current translations will be loaded from it)')

        parser.add_argument('--exclude-dir', '-x', default=[], dest='excluded_paths', action='append',
                            help='Paths to exclude. Default is none. Can be used multiple times. '
                                 'Works only with ChainExtractor.')


    def handle(self, *args, **options):
        if not (bool(options.get('app')) ^ bool(options.get('path'))):
            print bcolors.WARNING + 'You must choose only one of --app or --path' + bcolors.ENDC
            return

        if not options.get('tranz_dir') and (not options.get('app') or not settings.TRANZ_SEARCH_LOCALE_IN_APPS):
            print bcolors.WARNING + 'You must provide an --tranz-dir when in --path mode, or when TRANZ_SEARCH_LOCALE_IN_APPS ' \
                                    'settings variable is False.' + bcolors.ENDC
            return

        self.excluded_paths = [os.path.abspath(path) for path in options['excluded_paths']]
        self.excluded_paths += [os.path.abspath(django_translate.__path__[0])]
        self.locale = options['locale']
        self.verbosity = options['verbosity']

        # Find directories to scan
        if options.get('app'):
            for app in apps.app_configs.values():
                if app.name == options.get('app'):
                    current_name = app.name
                    root_path = app.path
                    break
            else:
                raise ValueError("App {0} not found".format(options.get('app')))
        else:
            root_path = os.path.abspath(options['path'])
            current_name = root_path.split("/")[-1]

        tranz_dir = options.get('tranz_dir') or os.path.join(root_path, 'tranz')

        print "Loading existing messages"
        current_catalogue = MessageCatalogue(options['locale'])
        loader = services.loader
        loader.load_messages(tranz_dir, current_catalogue)
        if len(current_catalogue.messages) == 0:
            print "No messages were loaded, make sure there actually are " \
                  "translation file in format {{catalog}}.{{locale}}.{{format}} in {0}".format(tranz_dir)
            return

        print "Extracting translations"
        translations = self.extract_translations(services.extractor, root_path)
        if len(translations) == 0:
            print "No messages were extracted, from {0} using {1}".format(root_path, services.extractor.__class__.__name__)
            return

        self.validate_translations(translations, current_catalogue)

    def extract_translations(self, extractor, root_path):
        if isinstance(extractor, extractors.ChainExtractor):
            subextractors = extractor._extractors.values()
        else:
            subextractors = [extractor]

        translations = []

        for subextractor in subextractors:
            if not isinstance(subextractor, extractors.BaseExtractor):
                print "Skipping extractor ", subextractor.__type__.__name__
                continue

            paths = subextractor.extract_files(root_path)
            paths = self.filter_exluded_paths(paths)
            print "scanning paths", paths
            for path in paths:
                try:
                    with open(path, 'r') as f:
                        batch = subextractor.extract_translations(f.read())
                        for t in batch:
                            t.file = path
                        translations += batch
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    msg = 'There was an exception in extractor {0} when processing ' \
                          'resource "{1}"'.format(type(subextractor).__name__, path)
                    msg = msg + "\nOriginal message: {0} {1}".format(exc_type.__name__, exc_value)
                    raise ValueError(msg), None, exc_traceback
        return translations

    def validate_translations(self, translations, current_catalogue):
        """
        @TODO: check if translation is present at all languages
        @TODO: check if all plural forms are present
        :param translations:
        @return:
        """
        self.flushed = 0

        file = None
        warnings = []
        for t in translations:
            if t.file != file:
                self.flush_warnings(file, warnings)
                warnings = []
                file = t.file

            if t.id.is_literal:
                domain = t.domain.value if t.domain and t.domain.is_literal else "messages"

                if not current_catalogue.has(t.id.value, domain):
                    warnings.append(['No such translation "{0}" in domain {1}'.format(t.id.value, domain), t])
                else:
                    formatter = Formatter()
                    formatter.format(current_catalogue.get(t.id.value, domain))

                    if len(formatter.used) and not t.parameters:
                        warnings.append(["No format variables passed, expected: {0}".format(", ".join(formatter.used)), t])

                    if len(formatter.used) and t.parameters and t.parameters.is_literal:
                        parameters = set(t.parameters.value)
                        if t.is_transchoice and t.number is not None:
                            parameters.add("count")

                        if formatter.used != parameters:
                            warnings.append(["Expected/received parameters mismatch, (expected: {0}), (received: {1})".format(
                                ", ".join(formatter.used), ", ".join(parameters)
                            ), t])

                    if t.is_transchoice and t.number is None:
                        warnings.append(['Transchoice "number" is missing', t])

            if t.id and not t.id.is_literal:
                warnings.append(["Translation of non-literal value", t])

            if t.parameters and not t.parameters.is_literal:
                warnings.append(["Variables passed via reference", t])
        self.flush_warnings(file, warnings)

        if self.flushed == 0:
            print bcolors.OKGREEN + "Scanned {0} translations and everything seems to be ok!".format(len(translations)) + bcolors.ENDC
        else:
            print bcolors.FAIL + "{0} problems found".format(self.flushed) + bcolors.ENDC

    def filter_exluded_paths(self, paths):
        valid = []
        for path in paths:
            for excluded in self.excluded_paths:
                if path.startswith(excluded):
                    break
            else:
                valid.append(path)
        return valid

    def flush_warnings(self, file, warnings):
        if not len(warnings):
            return

        self.flushed += len(warnings)

        lines = None
        if self.verbosity > 1:
            try:
                with open(file, 'r') as f:
                    lines = f.read().split("\n")
            except Exception, e:
                pass

        print bcolors.WARNING + "{0} warnings in file {1}".format(len(warnings), file) + bcolors.ENDC
        for msg, trans in warnings:
            print bcolors.WARNING + "line {0}: {1}".format(trans.lineno or "?", msg) + bcolors.ENDC
            if lines and self.verbosity > 1 and trans.lineno:
                print "{0}: {1}".format(trans.lineno, lines[trans.lineno-1])

        print ""

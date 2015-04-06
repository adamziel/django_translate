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

    help = """Extract translation strings from templates from a given location. It can display them or merge
              the new ones into the translation files. When new translation strings are found it can
              automatically add a prefix to the translation message.

              Example running against app folder
                  ./manage.py tranzdump -l en --path ./ --output-path ./tranz
                  ./manage.py tranzdump -l fr --force --prefix="new_" --app website --exclude ./website/static
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

        parser.add_argument('--output-dir', dest='output_dir', default=None, action='store',
                            help='Override the default output dir')

        parser.add_argument('--exclude-dir', '-x', default=[], dest='excluded_paths', action='append',
                            help='Paths to exclude. Default is none. Can be used multiple times. '
                                 'Works only with ChainExtractor.')

        parser.add_argument('--prefix', dest='prefix', default="__", action='store',
                            help='Override the default prefix')

        parser.add_argument('--format', dest='format', default="yml", action='store',
                            help='Override the default output format')

        parser.add_argument('--dump-messages', dest='dump_messages', action='store_true',
                            help='Should the messages be dumped in the console')

        parser.add_argument('--force', dest='force', action='store_true',
                            help='Should the update be done')

        parser.add_argument('--no-backup', dest='no_backup', action='store_true',
                            help='Should backup be disabled')

        parser.add_argument('--clean', dest='clean', default=False, action='store_true',
                            help='Should clean not found messages',)

    def handle(self, *args, **options):
        if options.get('force') != True and options.get('dump_messages') != True:
            print bcolors.WARNING + 'You must choose at least one of --force or --dump-messages' + bcolors.ENDC
            return

        if not (bool(options.get('app')) ^ bool(options.get('path'))):
            print bcolors.WARNING + 'You must choose only one of --app or --path' + bcolors.ENDC
            return

        if not options.get('output_dir') and (not options.get('app') or not settings.TRANZ_SEARCH_LOCALE_IN_APPS):
            print bcolors.WARNING + 'You must provide an --output-dir when in --path mode, or when TRANZ_SEARCH_LOCALE_IN_APPS ' \
                                    'settings variable is False.' + bcolors.ENDC
            return

        self.excluded_paths = [os.path.abspath(path) for path in options['excluded_paths']]

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

        output_dir = options.get('output_dir') or os.path.join(root_path, 'tranz')
        writer = services.writer

        print 'Generating "{0}" translation files for "{1}"'.format(options.get('locale'), current_name)

        print "Loading existing messages"
        current_catalogue = MessageCatalogue(options['locale'])
        loader = services.loader
        loader.load_messages(output_dir, current_catalogue)
        if len(current_catalogue.messages) == 0:
            print "No messages were loaded, make sure there actually are " \
                  "translation file in format {{catalog}}.{{locale}}.{{format}} in {0}".format(output_dir)
            return

        print "Extracting messages"
        extracted_catalogue = MessageCatalogue(options['locale'])
        extractor = services.extractor
        extractor.set_prefix(options['prefix'])
        self.extract_messages(extractor, root_path, extracted_catalogue)

        print "Processing catalogues"
        operation_class = operations.DiffOperation if options['clean'] else operations.MergeOperation
        operation = operation_class(current_catalogue, extracted_catalogue)

        if not len(operation.get_domains()):
            print "No translations found"
            return

        if options["dump_messages"]:
            for domain in operation.get_domains():
                print "Displaying messages for domain {0}".format(domain)
                new_keys = operation.get_new_messages(domain).keys()
                all_keys = operation.get_messages(domain).keys()
                for id in set(all_keys).difference(new_keys):
                    print id

                for id in new_keys:
                    print bcolors.OKGREEN + id + bcolors.ENDC

                for id in operation.get_obsolete_messages(domain).keys():
                    print bcolors.FAIL + id + bcolors.ENDC

        if options["no_backup"]:
            writer.disable_backup()

        if options["force"]:
            print "Writing files to {0}".format(output_dir)
            writer.write_translations(operation.get_result(), options['format'], {
                "path": output_dir,
                "default_locale": options['locale']
            })

    def extract_messages(self, extractor, root_path, extracted_catalogue):
        if isinstance(extractor, extractors.ChainExtractor):
            subextractors = extractor._extractors.values()
        else:
            subextractors = [extractor]

        for subextractor in subextractors:
            if not isinstance(subextractor, extractors.BaseExtractor):
                subextractor.extract(root_path, extracted_catalogue)
                continue

            paths = subextractor.extract_files(root_path)
            paths = self.filter_exluded_paths(paths)
            for path in paths:
                try:
                    subextractor.extract([path], extracted_catalogue)
                except Exception, e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    msg = 'There was an exception in extractor {0} when processing ' \
                          'resource "{1}"'.format(type(subextractor).__name__, path)
                    msg = msg + "\nOriginal message: {0} {1}".format(exc_type.__name__, exc_value)
                    raise ValueError(msg), None, exc_traceback

    def filter_exluded_paths(self, paths):
        valid = []
        for path in paths:
            for excluded in self.excluded_paths:
                if path.startswith(excluded):
                    break
            else:
                valid.append(path)
        return valid

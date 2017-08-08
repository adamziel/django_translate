# -*- coding: utf-8 -*-

try:
    from django.utils.deprecation import MiddlewareMixin as BaseClass
except ImportError:
    BaseClass = object

from django_translate.services import translator as django_translator

class LocaleMiddleware(BaseClass):
    """
    This is a very simple middleware that parses a request
    and decides what locale to activate in current django_translator
    """
    def process_request(self, request):
        if not hasattr(request, 'LANGUAGE_CODE'):
            raise RuntimeError('django.middleware.locale.LocaleMiddleware is required '
                               'in order to use django_translate.middleware.LocaleMiddleware ')
        django_translator.locale = request.LANGUAGE_CODE

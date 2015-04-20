# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re
import json
from functools import partial
from django import template
from django.core.urlresolvers import reverse as _reverse
from django.template import Library, Node, TemplateSyntaxError
from django.template.base import VariableDoesNotExist
from django.template.loader import render_to_string
from django_translate.services import translator
from django_translate import settings

register = Library()


def tranz(parser, token, is_transchoice=False):
    """
    Templatetagish wrapper for Translator.trans()

    :param parser:
    :param token:
    :param is_transchoice:
    :return:
    """
    tokens = token.split_contents()
    id = tokens[1]
    number = domain = locale = None
    parameters = {}
    if len(tokens) > 2:
        skip_idx = None
        for idx, token in enumerate(tokens[2:], start=2):
            if idx == skip_idx:
                skip_idx = None
                continue

            if "=" in token:
                k, v = token[0:token.index('=')], token[token.index('=') + 1:]
                parameters[k] = v
            elif token == "number":
                number = tokens[idx + 1]
                skip_idx = idx + 1
            elif token == "from":
                domain = tokens[idx + 1]
                skip_idx = idx + 1
            elif token == "into":
                locale = tokens[idx + 1]
                skip_idx = idx + 1
            else:
                raise TemplateSyntaxError(
                    "Unexpected token {0} in tag tranz".format(token))
    if is_transchoice and number is None:
        raise TemplateSyntaxError(
            "number parameter expected in tag {tag_name}")

    return TranzNode(
        id,
        parameters,
        domain,
        locale,
        number,
        is_transchoice=is_transchoice)

register.tag("tranz", tranz)
register.tag("tranzchoice", partial(tranz, is_transchoice=True))


class TranzNode(Node):

    def __init__(self, id, parameters, domain, locale, number=None, is_transchoice=False):
        self.id = template.Variable(id)
        self.parameters = {
            k: template.Variable(v) for k, v in parameters.items()
        }
        self.domain = domain
        self.locale = locale
        self.is_transchoice = is_transchoice
        self.number = number if is_transchoice else None
        super(TranzNode, self).__init__()

    def render(self, context):
        prefix = context.get("tranz_prefix", "")
        if prefix:
            prefix += "_"
        id = prefix + self.id.resolve(context)

        parameters = {}
        for k, v in self.parameters.items():
            try:
                parameters[k] = v.resolve(context)
            except VariableDoesNotExist, e:
                parameters[k] = ""

        domain = template.Variable(self.domain).resolve(context) if self.domain is not None \
                        else context.get('tranz_domain', None)
        locale = template.Variable(self.locale).resolve(context) if self.locale is not None \
                        else context.get('tranz_locale', None)
        number = template.Variable(self.number).resolve(context) if self.number is not None else None

        if locale is None:
            # Try to use LocaleMiddleware if it's on

            is_request_context = isinstance(context, template.RequestContext)
            if is_request_context and hasattr(context, "request") and hasattr(context.request, 'LANGUAGE_CODE'):
                locale = context.request.LANGUAGE_CODE

        if locale is None:
            locale = settings.TRANZ_DEFAULT_LANGUAGE
            
        if self.is_transchoice:
            return translator.transchoice(
                id,
                number,
                parameters,
                domain,
                locale
            )
        else:
            return translator.trans(id, parameters, domain, locale)


@register.tag
def tranz_context(parser, token):
    """
    Templatetagish wrapper for Translator.transchoice()
    """
    tokens = token.split_contents()

    parameters = {}
    for idx, token in enumerate(tokens[1:], start=1):
        if "=" in token:
            if token[0:token.index('=')] not in ("domain", "prefix", "locale"):
                raise TemplateSyntaxError(
                    "Unexpected token {0} in tag {{tag_name}}".format(token)
                )

            k, v = token[0:token.index('=')], token[token.index('=') + 1:]
            parameters[k] = v
        else:
            raise TemplateSyntaxError(
                "Unexpected token {0} in tag {{tag_name}}".format(token))

    return TranzContextNode(
        parameters.get('prefix', None),
        parameters.get('domain', None),
        parameters.get('locale', None)
    )


class TranzContextNode(Node):

    def __init__(self, prefix, domain, locale):
        self.prefix = prefix
        self.domain = domain
        self.locale = locale
        super(TranzContextNode, self).__init__()

    def render(self, context):
        if self.prefix is not None:
            context['tranz_prefix'] = template.Variable(self.prefix).resolve(context)

        if self.domain is not None:
            context['tranz_domain'] = template.Variable(self.domain).resolve(context)

        if self.locale is not None:
            context['tranz_locale'] = template.Variable(self.locale).resolve(context)
        return ""

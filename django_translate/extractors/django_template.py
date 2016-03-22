# -*- coding: utf-8 -*-

import re
import os
from django.template.base import Lexer, TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK
from python_translate.extractors.base import Translation, TransVar, ExtensionBasedExtractor

val = '''(?:[^"' ]+)|(?:"[^"]*?")|(?:'[^']*?')'''

id_re = re.compile(r"^tranz(?:choice)?\s*({0})".format(val))
number_re = re.compile(r"number\s*({0})".format(val))
domain_re = re.compile(r"from\s*({0})".format(val))
locale_re = re.compile(r"into\s*({0})".format(val))
properties_re = re.compile(r"(?:\s+\w+=(?:{0}))".format(val))


class DjangoTemplateExtractor(ExtensionBasedExtractor):

    def __init__(
            self,
            file_extensions=None,
            tranz_tag=None,
            tranzchoice_tag=None):
        file_extensions = file_extensions if file_extensions is not None else (
            "*.html",
            "*.txt")

        self.tranz_tag = tranz_tag if tranz_tag is not None else 'tranz'
        self.tranzchoice_tag = tranzchoice_tag if tranzchoice_tag is not None else 'tranzchoice'
        super(DjangoTemplateExtractor, self).__init__(file_extensions=file_extensions)

    def extract_translations(self, string):
        """Extract messages from Django template string."""

        trans = []
        for t in Lexer(string.decode("utf-8"), None).tokenize():
            if t.token_type == TOKEN_BLOCK:
                if not t.contents.startswith(
                        (self.tranz_tag, self.tranzchoice_tag)):
                    continue

                is_tranzchoice = t.contents.startswith(
                    self.tranzchoice_tag +
                    " ")
                kwargs = {
                    "id": self._match_to_transvar(id_re, t.contents),
                    "number": self._match_to_transvar(number_re, t.contents),
                    "domain": self._match_to_transvar(domain_re, t.contents),
                    "locale": self._match_to_transvar(locale_re, t.contents),
                    "is_transchoice": is_tranzchoice, "parameters": TransVar(
                        [x.split("=")[0].strip() for x in properties_re.findall(t.contents) if x],
                        TransVar.LITERAL
                    ),
                    "lineno": t.lineno,
                }

                trans.append(Translation(**kwargs))
        return trans

    def _match_to_transvar(self, reg, string, default=""):
        match = reg.findall(string)
        return self._to_transvar(match[0] if match else default)

    def _to_transvar(self, val):
        if val is None:
            return None

        if len(val) > 0 and (val[0] in ('"', "'") or val.isdigit()):
            if val[0] in ('"', "'"):
                val = val[1:-1]
            return TransVar(val, TransVar.LITERAL)
        else:
            return TransVar(val, TransVar.VARNAME)

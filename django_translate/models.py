
from django_translate import settings
from django_translate.services import monkeypatch_django

if settings.TRANZ_REPLACE_DJANGO_TRANSLATIONS:
    monkeypatch_django()

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    url(r'^$', 'example_basic.translate.views.hello', name='hello'),
    url(r'^apples$', 'example_basic.translate.views.apples', name='apples'),
    url(r'^apples/python$', 'example_basic.translate.views.pythonic_apples', name='pythonic_apples'),
    url(r'^po', 'example_basic.translate.views.po', name='po'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

from django.conf.urls import include, url

urlpatterns = [
    # Examples:
    url(r'^$', 'example_dropin.translate.views.hello', name='hello'),
    url(r'^apples$', 'example_dropin.translate.views.apples', name='apples'),
    url(r'^apples/python$', 'example_dropin.translate.views.pythonic_apples', name='pythonic_apples'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader

from django.utils.translation import ugettext, ungettext

def hello(request):
    return render_to_response("hello.html", context=RequestContext(request))

def apples(request):
    return render_to_response("apples.html", context=RequestContext(request))

def pythonic_apples(request):
    return render_to_response("apples_python.html", {"rendered": 
        u"<h1>{0}</h1>"
        "<p>{1}</p>"
        "<p>{2}</p>"
        "<p>{3}</p>".format(
            ugettext("apples.header"),
            ugettext("apples.want_some_%(fruits)s") % {"fruits": "apples"},
            ungettext("I've had one apple and it was great",
                      "I've had %(counter)s apples and it was great",
                      1) % {"counter": 1},
            ungettext("I've had one apple and it was great",
                      "I've had %(counter)s apples and it was great",
                      3) % {"counter": 3}
        )
    })
            
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader

from django_translate.services import trans as _, transchoice

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
            _("apples.header"),
            _("apples.want_some", {"fruits": "apples"}),
            transchoice("apples.praise_n", 1),
            transchoice("apples.praise_n", 3)
        )
    })

def po(request):
    return render_to_response("po.html", context=RequestContext(request))

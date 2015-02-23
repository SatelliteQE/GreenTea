#coding: utf-8

from django.conf import settings

def basic(request):
    #admin
    if request.META["PATH_INFO"] in ("admin",):
        return {}

    data = {
        "version": settings.VERSION,
        "footer": settings.TEMPLATE_FOOTER,
        "conf" : {
        	"BEAKER_SERVER": settings.BEAKER_SERVER,
        }
    }

    return data

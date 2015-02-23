#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013


from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from models import Performance

@csrf_exempt
def performance(request):
	perf = Performance(
				label=request.POST.get("label"),
				name=request.POST.get("name"), 
				description=request.POST.get("description"),
				exitcode=request.POST.get("exitcode", -1),
				duration=request.POST.get("duration")
			)
	perf.save()
	data = "ok"
	return HttpResponse(data, mimetype="application/json")

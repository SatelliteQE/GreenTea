# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import json
import logging
from datetime import date, datetime, timedelta

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from apps.core.forms import GroupsForm, JobForm
from apps.core.models import (FAIL, NEW, WAIVED, WARN, Author, CheckProgress,
                              EnumResult, Job, JobTemplate, Recipe,
                              RecipeTemplate, Task, Test, TestHistory)
from apps.core.utils.beaker import JobGen
from apps.core.utils.beaker_import import Parser
from apps.core.utils.date_helpers import TZDatetime
from apps.taskomatic.models import TaskPeriodSchedule
from apps.waiver.models import Comment

logger = logging.getLogger(__name__)


@login_required
def import_xml(request):
    # TODO: rewrite to standard View Class
    data = {}
    if request.POST and "textxml" in request.POST:
        xml = request.POST["textxml"].strip()
        s = Parser(content=xml)
        if not s.status:
            data["error"] = s.error
        else:
            s.run()
            data["xml"] = xml
            data["job"] = s.job
            data["recipes"] = RecipeTemplate.objects.filter(jobtemplate=s.job)

    return render(request, 'import_xml.html', data)


def import_group(request):
    # TODO: rewrite to standard View Class
    data = {"forms": GroupsForm()}
    if request.POST and "group" in request.POST:
        forms = GroupsForm(request.POST)
        if forms.is_valid():
            data["group"] = forms.save()
        data["forms"] = forms
    return render(request, 'import_group.html', data)


def get_xml(jobT):
    """Takes JobTemplate object and returns its prettified job XML"""
    jobG = JobGen()
    xml = jobG.getXML(jobT, reserve=True)
    soup = BeautifulSoup(xml, "xml")
    return soup.prettify()


def to_xml(request, id):
    # TODO: rewrite to standard View Class
    try:
        jobT = JobTemplate.objects.get(id=id)
    except JobTemplate.DoesNotExist:
        raise Http404
    xml = get_xml(jobT)
    return render(request, 'job_xml.html',
                  {'template': jobT, "xml": xml, "beaker": settings.BEAKER_SERVER})


def create_matrix(days):
    datearray = []
    index = 0
    while True:
        index += 1
        newday = date.today() - timedelta(days=index)
        # suturday and sunday were ignored
        if newday.weekday() in (4, 5):
            continue
        datearray.append(newday)  # .strftime("%Y-%m-%d"))
        if len(datearray) == days:
            break
    return list(reversed(datearray))


def statistic(request):
    content = "TODO"
    # we need create statistic page
    return HttpResponse(content, content_type='text/plain')

# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import hashlib
import logging
import sys
from copy import copy
from datetime import datetime, timedelta

from django.conf import settings
from django.db import connection
from django.db.models import Count
from django.http import HttpResponse
from django.views.generic import TemplateView
from taggit.models import Tag

from apps.core.forms import FilterForm
from apps.core.models import (RESULT_CHOICES, Author, CheckProgress, Event,
                              JobTemplate, Recipe, render_label)
from apps.taskomatic.models import TaskPeriodSchedule
from apps.waiver.forms import WaiverForm
from apps.waiver.models import Comment
from base import create_matrix

logger = logging.getLogger(__name__)


class JobsDiffView(TemplateView):
    template_name = 'diffs.html'

    def dispatch(self, request, *args, **kwargs):
        self.filters = {}
        self.forms = {}
        return super(JobsDiffView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        if 'jobs' in self.forms:
            context["form"] = self.forms['jobs']
        else:
            context["form"] = JobForm()
        return context

    def formEvent(self, parametrs):
        jobform = JobForm(parametrs)
        self.forms['jobs'] = jobform

    def post(self, request, *args, **kwargs):
        self.formEvent(request.POST)
        context = self.get_context_data(**kwargs)

        if self.forms['jobs'].is_valid():
            context["diff"] = self.forms['jobs'].compare()

        return self.render_to_response(context)

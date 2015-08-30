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


class JobDetailView(TemplateView):
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        job_id = kwargs["id"]
        oJobTmp = JobTemplate.objects.get(id=job_id)
        jobs_list = Job.objects.filter(template=oJobTmp).order_by("-date")

        paginator = Paginator(jobs_list, settings.PAGINATOR_OBJECTS_ONPAGE)
        jobs = paginator.page(int(self.request.GET.get('page', 1)))

        context.update({
            "jobtemplate": oJobTmp,
            "jobs": jobs,
            "paginator": paginator,
        })
        return context

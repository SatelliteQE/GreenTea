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


class TestDetailView(TemplateView):
    template_name = 'test-detail.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        test_id = kwargs["id"]
        oTest = Test.objects.get(id=test_id)
        task_list = Task.objects.filter(
            test=oTest).order_by("-recipe__job__date")

        paginator = Paginator(task_list, settings.PAGINATOR_OBJECTS_ONPAGE)
        tasks = paginator.page(int(self.request.GET.get('page', 1)))

        context.update({
            "jobtemplate": oTest,
            "tasks": tasks,
            "paginator": paginator
        })
        return context

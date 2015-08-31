# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import logging

from django.conf import settings
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from apps.core.models import (Task, Test)

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

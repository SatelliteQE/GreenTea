# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import logging
from datetime import datetime

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import TemplateView

from apps.core.models import CheckProgress, EnumResult, Task, TestHistory
from apps.taskomatic.models import TaskPeriodSchedule
from apps.waiver.models import Comment

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = 'homepage.html'
    filters = {}
    forms = {}

    def get_network_stas(self, **kwargs):
        def get_lab(hostname, num):
            return ".".join(hostname.split(".")[-1 * num:])

        # TODO - show only some last runs
        periods = TaskPeriodSchedule.objects.all().values(
            "title", "date_create", "id", "counter").order_by("title", "-date_create")
        ids = map(lambda x: x["id"], periods)

        tasks = Task.objects.filter(recipe__job__schedule_id__in=ids) \
            .values("result", "recipe__system__hostname", "recipe__job__schedule__id") \
            .annotate(results=Count("result"),
                      hosts=Count("recipe__system__hostname"),
                      label=Count("recipe__job__schedule")) \
            .order_by("recipe__system__hostname", "recipe__job__schedule__id")

        data = {}
        labels = set()
        ER = EnumResult()
        for it in tasks:
            hostname = get_lab(it.get("recipe__system__hostname"), 4)
            schedule = it.get("recipe__job__schedule__id")
            result, count = ER.get(it.get("result")), it.get("hosts")
            labels.add(schedule)
            if hostname in data:
                if schedule not in data[hostname]:
                    data[hostname].update({schedule: {result: count}})
                data[hostname][schedule][result] = count
            else:
                data[hostname] = {schedule: {result: count}}

        for hostname, value in data.items():
            for schedule in labels:
                if not value.get(schedule):
                    data[hostname][schedule] = {}
        return {"labels": labels, "data": data}

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        try:
            context['progress'] = CheckProgress.objects.order_by(
                "-datestart")[0]
        except IndexError:
            context['progress'] = None
        # Waiver
        comments = Comment.objects\
            .filter(created_date__gt=datetime.today().date())\
            .order_by("-created_date", "task", "recipe", "job")
        paginator = Paginator(comments, settings.PAGINATOR_OBJECTS_ONHOMEPAGE)
        context['waiver'] = paginator.page(
            int(self.request.GET.get('cpage', 1)))
        context['cpaginator'] = paginator
        history = TestHistory.objects.filter().order_by(
            "-date")[:settings.PAGINATOR_OBJECTS_ONHOMEPAGE * 10]
        paginator = Paginator(history, settings.PAGINATOR_OBJECTS_ONHOMEPAGE)
        context['history'] = paginator.page(
            int(self.request.GET.get('hpage', 1)))
        context['hpaginator'] = paginator

        context['networking'] = self.get_network_stas()
        return context

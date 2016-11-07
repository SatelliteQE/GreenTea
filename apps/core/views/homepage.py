# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import logging
from datetime import datetime

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import TemplateView
from elasticsearch import Elasticsearch

from apps.core.forms import HomepageForm
from apps.core.models import (CheckProgress, EnumResult, FileLog, Task,
                              TestHistory)
from apps.report.models import Score
from apps.taskomatic.models import TaskPeriodList, TaskPeriodSchedule
from apps.waiver.models import Comment

logger = logging.getLogger(__name__)


class PaganatorSearch:

    def __init__(self, count_objs):
        self.objects = range(count_objs / 10)

    def page(self, page):
        self.actual_page = page
        if page == 1:
            self.has_previous = False
        else:
            self.has_previous = True
            self.previous_page_number = page - 1

        if len(self.objects) < page:
            self.has_next = False
        else:
            self.has_next = True
            self.next_page_number = page + 1
        return self


class HomePageView(TemplateView):
    template_name = 'homepage.html'
    filters = {}
    forms = {}
    es = Elasticsearch(settings.ELASTICSEARCH)

    def search(self):
        query = self.filters.get("search")
        page = self.filters.get("page")

        if not page:
            page = 1
        if query:
            result = self.es.search(index="testout.log", body={
                "query":
                    {"match":
                        {
                            "content": {
                                "query": "'%s'" % query,
                                "type": "phrase",
                            }
                        }
                     },
                "sort":
                    {"period": "desc"},
                "from": 10 * (page - 1),
                "size": 10
            },
                fields=("_id", "task", "path", "recipe", "period"),
            )
            ids = [int(x["_id"]) for x in result["hits"]["hits"]]

            dict_tmp = dict((x, None) for x in ids)
            for it in FileLog.objects.filter(index_id__in=ids):
                dict_tmp[it.id] = it
            result["result"] = []
            for _id in ids:
                result["result"].append(dict_tmp[_id])
            sp = PaganatorSearch(result["hits"]["total"])
            result["paginator"] = sp.page(page)
            return result

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

        form = HomepageForm(self.request.GET)
        form.is_valid()
        context["forms"] = form
        self.filters = form.cleaned_data
        pag_type = self.request.GET.get('type')

        if settings.ELASTICSEARCH:
            if self.es.ping():
                context["elasticsearch"] = self.es.info()
            context['search'] = self.search()
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

        history = TestHistory.objects.filter().order_by(
            "-date")[:settings.PAGINATOR_OBJECTS_ONHOMEPAGE * 10]
        paginator = Paginator(history, settings.PAGINATOR_OBJECTS_ONHOMEPAGE)
        context['history'] = paginator.page(
            int(self.request.GET.get('hpage', 1)))

        # context['networking'] = self.get_network_stas()
        ids = [it["max_id"] for it in TaskPeriodList.last_runs()]
        filter_ids = ids
        if self.filters.get("schedule"):
            filter_ids = [int(self.filters.get("schedule"))]
        order = self.filters.get(
            "order") if self.filters.get("order") else "score"

        # Score
        score_obj = Score.objects.filter(
            schedule__in=filter_ids).order_by(order)
        score = Paginator(score_obj, settings.PAGINATOR_OBJECTS_ONHOMEPAGE)

        page = 1
        if "score" == pag_type:
            page = int(self.filters.get('page', 1))
        context["score"] = score.page(int(page))
        range_min = page - 5
        range_range = 10
        if page <= range_range / 2:
            range_min = 1
            range_range += page
        if score.page_range[-1] < range_min + range_range:
            range_min = score.page_range[-1] - range_range
        context["score"].ranges = sorted(set(
            [1, page, score.page_range[-1]]).union(range(range_min, range_min + range_range)))

        context["schedules"] = TaskPeriodSchedule.objects.filter(
            id__in=ids).order_by("period")

        context["files"] = {
            "indexed": FileLog.objects.filter(is_indexed=False, is_downloaded=True).count(),
            "downloaded": FileLog.objects.filter(status_code=0).count()
        }
        return context

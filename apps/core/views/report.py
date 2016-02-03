# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 3.2.2016

from django.views.generic import TemplateView
from apps.core.models import GroupTestTemplate, Test, Task
from django.db.models import Max, Count
from apps.taskomatic.models import TaskPeriodSchedule
from collections import defaultdict


class ReportListView(TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        periods = TaskPeriodSchedule.objects.values("period")\
            .annotate(dmax=Max('id'))

        ids = [it["dmax"] for it in periods]
        tasks = Task.objects.filter(recipe__job__schedule__id__in=ids)\
            .values("result", "recipe__job__schedule__title")\
            .annotate(dcount=Count("result"), scount=Count("recipe__job__schedule"))\
            .order_by("result")

        context["grouptest"] = GroupTestTemplate.objects.values(
            "group__name").annotate(dcount=Count("group")).order_by("-dcount")
        context["repotest"] = Test.objects.values("git__name").annotate(
            dcount=Count("git")).order_by("-dcount")
        test_ids = Task.objects.filter(recipe__job__schedule__id__in=ids)\
            .values("test__id").annotate(dcount=Count("test")).order_by("-dcount")
        ids = [it["test__id"] for it in test_ids]
        repotask = Test.objects.filter(id__in=ids).values(
            "git__name").annotate(dcount=Count("git")).order_by("-dcount")

        keys = dict([(it["git__name"], it["dcount"]) for it in repotask])

        for it in context["repotest"]:
            if it["git__name"] in keys:
                it.update({"run": keys[it["git__name"]]})
                it.update({"notrun": it["dcount"] - keys[it["git__name"]]})

        t = {}
        for it in tasks:
            key = it["recipe__job__schedule__title"]
            if not key in t.keys():
                t[key] = {}
            t[key].update({it["result"]: it["dcount"]})
        context["tasks"] = t

        return context

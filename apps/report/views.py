# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 3.2.2016

from django.views.generic import TemplateView
from apps.core.models import GroupTestTemplate, Test, Task
from django.db.models import Max, Count
from apps.taskomatic.models import TaskPeriodSchedule, TaskPeriodList
from apps.report.models import ReportList


class ListId:

    @staticmethod
    def running(schedule_ids):
        test_ids = Task.objects\
            .filter(recipe__job__schedule__id__in=schedule_ids)\
            .values("test__id")\
            .annotate(dcount=Count("test"))\
            .order_by("-dcount")
        return [it["test__id"] for it in test_ids]


class ReportListView(TemplateView):
    template_name = 'report.html'

    def get(self, request, *args, **kwargs):
        self.repo = request.GET.get("repo")
        return super(self.__class__, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        ids = [it["max_id"] for it in TaskPeriodList.last_runs()]
        tasks = Task.objects.filter(recipe__job__schedule__id__in=ids)\
            .values("result", "recipe__job__schedule__title")\
            .annotate(dcount=Count("result"), scount=Count("recipe__job__schedule"))\
            .order_by("result")

        context["grouptest"] = GroupTestTemplate.objects.values(
            "group__name").annotate(dcount=Count("group")).order_by("-dcount")
        context["repotest"] = Test.objects.values("git__name").annotate(
            dcount=Count("git")).order_by("-dcount")

        running_ids = ListId.running(ids)
        repotask = Test.objects.filter(id__in=running_ids).values(
            "git__name").annotate(dcount=Count("git")).order_by("-dcount")

        keys = dict([(it["git__name"], it["dcount"]) for it in repotask])

        for it in context["repotest"]:
            if it["git__name"] in keys:
                it.update({"run": keys[it["git__name"]]})
                it.update({"notrun": it["dcount"] - keys[it["git__name"]]})

        t = {}
        for it in tasks:
            key = it["recipe__job__schedule__title"]
            if key not in t:
                t[key] = {}
            t[key].update({it["result"]: it["dcount"]})
        context["tasks"] = t

        if self.repo:
            context["nonrun"] = Test.objects.filter(
                is_enable=True, git__name=self.repo).exclude(id__in=running_ids)

        #context["reports"] = Report.objects.filter(is_enabled=True)

        report = ReportList(ids)
        # get statistic about tests
        report.stat_tests()
        # get statistic about last runs
        report.stat_tasks()
        context["reports"] = report
        return context

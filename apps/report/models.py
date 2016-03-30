from django.db import models
from apps.core.models import JobTemplate, TaskTemplate, Task, EnumResult
from apps.taskomatic.models import TaskPeriodList
from django.db.models import Count


class Report(models.Model):
    name = models.CharField(max_length=64)
    jobs = models.ManyToManyField(JobTemplate)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", ]

    def __unicode__(self):
        return "%s" % self.name


class ReportList:

    def __init__(self, periods=None):
        self.periods = periods
        self.reports = Report.objects.all()

    def __iter__(self):
        for it in self.reports:
            yield it

    def stat_tasks(self):
        for report in self.reports:
            data = Task.objects.filter(
                recipe__job__template__is_enable=True,
                recipe__job__template__in=report.jobs.all(),
                recipe__job__schedule__in=self.periods,
            )\
                .values("result").annotate(dcount=Count("result")).order_by("result")

            er = EnumResult()
            for it in data:
                it["name"] = er.get(it["result"])
            report.tasks = data

    def stat_tests(self):
        for report in self.reports:
            report.tests = TaskTemplate.objects.filter(
                recipe__jobtemplate__is_enable=True,
                recipe__jobtemplate__in=report.jobs.all()).distinct("test").count()

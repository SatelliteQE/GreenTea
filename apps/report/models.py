#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik <pstudeni@redhat.com>
# Year: 2016

import json

from django.db import models
from django.db.models import Count

from apps.core.models import (EnumResult, JobTemplate, RecipeTemplate, Task,
                              TaskTemplate, Test)
from apps.taskomatic.models import TaskPeriodList, TaskPeriodSchedule


class Report(models.Model):
    name = models.CharField(max_length=64)
    jobs = models.ManyToManyField(JobTemplate)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", ]

    def __unicode__(self):
        return "%s" % self.name


class Score(models.Model):
    test = models.ForeignKey(Test, db_index=True)
    schedule = models.ForeignKey(TaskPeriodSchedule, db_index=True)
    score = models.IntegerField(default=0)
    rate = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    result = models.TextField(blank=True)

    def get_result(self):
        result = json.loads(self.result)
        data = {"count": self.count}
        er = EnumResult()
        for it in result:
            data[er.get(it["result"])] = (it["count"] * 100) / self.count
        return data


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

    def stat_recipes(self):
        for report in self.reports:
            report.recipes = RecipeTemplate.objects.filter(
                jobtemplate__is_enable=True,
                jobtemplate__in=report.jobs.all()
            ).count()

    def stat_tests(self):
        for report in self.reports:
            report.tests = TaskTemplate.objects.filter(
                recipe__jobtemplate__is_enable=True,
                recipe__jobtemplate__in=report.jobs.all()).distinct("test").count()

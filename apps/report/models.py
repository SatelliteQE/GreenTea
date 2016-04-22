#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik <pstudeni@redhat.com>
# Year: 2016

import json

from django.db import models
from django.db.models import Count, permalink
from apps.core.models import (EnumResult, JobTemplate, RecipeTemplate, Task,
                              TaskTemplate, Test)
from apps.taskomatic.models import TaskPeriodList, TaskPeriodSchedule


class Report(models.Model):
    name = models.CharField(max_length=64)
    jobs = models.ManyToManyField(JobTemplate)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", ]
        app_label = "report"

    def __unicode__(self):
        return "%s" % self.name


class Score(models.Model):
    test = models.ForeignKey(Test, db_index=True)
    schedule = models.ForeignKey(TaskPeriodSchedule, db_index=True)
    score = models.IntegerField(default=0)
    rate = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    result = models.TextField(blank=True)

    class Meta:
        app_label = "report"

    def get_result_percent(self):
        result = json.loads(self.result)
        data = {"count": self.count}
        er = EnumResult()
        for it in result:
            data[er.get(it["result"])] = (it["count"] * 100) / self.count
        return data

    def get_result(self):
        result = json.loads(self.result)
        data = {"count": self.count}
        er = EnumResult()
        for it in result:
            data[er.get(it["result"])] = it["count"]
        return data


class ExternalPage(models.Model):
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=256)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        app_label = "report"

    def __unicode__(self):
        return "%s" % self.name

    @permalink
    def get_absolute_url(self):
        return ("report-page", [self.id, ])


class ReportList:

    def __init__(self, periods=None):
        self.period_ids = periods
        self.reports = Report.objects.all()
        self.periods = TaskPeriodSchedule.objects.filter(
            id__in=self.period_ids)

    def __iter__(self):
        for it in self.reports:
            yield it

    def stat_tasks(self):
        er = EnumResult()
        pass_test = Score.objects.filter(
            schedule__in=self.period_ids,
            rate__gt=1.9
        ).values("test__id")
        test_ids = [x["test__id"] for x in pass_test]

        for report in self.reports:
            fail = Task.objects.filter(
                recipe__job__template__is_enable=True,
                recipe__job__schedule__in=self.period_ids,
                recipe__job__template__in=report.jobs.all(),
                result=er.FAIL,
            ).distinct("test").count()

            passs = Task.objects.filter(
                recipe__job__template__is_enable=True,
                recipe__job__schedule__in=self.period_ids,
                recipe__job__template__in=report.jobs.all(),
                test__id__in=test_ids
            ).distinct("test").count()

            report.tests = Task.objects.filter(
                recipe__job__template__is_enable=True,
                recipe__job__schedule__in=self.period_ids,
                recipe__job__template__in=report.jobs.all(),
            ).distinct("test").count()

            report.tasks = [
                {"name": "fail", "dcount": int(fail)},
                {"name": "pass", "dcount": int(passs)},
                {"name": "warning", "dcount": int(
                    report.tests - passs - fail)},
            ]

    def stat_recipes(self):
        for report in self.reports:
            report.recipes = RecipeTemplate.objects.filter(
                jobtemplate__is_enable=True,
                jobtemplate__in=report.jobs.all()
            ).count()

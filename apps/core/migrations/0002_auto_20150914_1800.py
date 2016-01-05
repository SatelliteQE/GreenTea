# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models, transaction
from django.utils.timezone import utc
from apps.core.models import Job, JobTemplate
from apps.taskomatic.models import TaskPeriodSchedule, TaskPeriod


def migrate_chedule(label, period):
    tp = TaskPeriod.objects.get(label=label)

    tpl_jobs = JobTemplate.objects.filter(period=period)
    for it in tpl_jobs:
        it.schedule = tp
        it.save()

    for it in Job.objects.filter(template__period=period).order_by("date"):
        try:
            tps = TaskPeriodSchedule.objects.get(period=tp, date_create__year=it.date.year, date_create__month=it.date.month, date_create__day=it.date.day)
        except TaskPeriodSchedule.DoesNotExist:
            tps = TaskPeriodSchedule(title=label, date_create=it.date, period=tp)
            it.counter = TaskPeriodSchedule.objects.filter().count()
            tps.save()
        it.schedule = tps
        it.save()

    tp.recount_all()

def migrate_data(apps, schema_editor):
    for taskperiod in TaskPeriod.objects.all():
        if taskperiod.label == "daily-automation":
            migrate_chedule(taskperiod.label, JobTemplate.DAILY)
        elif taskperiod.label == "weekly-automation":
            migrate_chedule(taskperiod.label, JobTemplate.WEEKLY)

def unmigrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('taskomatic', '0002_taskperiod_position'),
    ]

    operations = [
        migrations.RunPython(migrate_data, unmigrate_data, atomic=False),
    ]

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

    s = set([it.date_create.date() for it in TaskPeriodSchedule.objects.filter(period=tp)])

    for it in Job.objects.filter(template__period=0).order_by("date"):
        date = it.date.date()
        if date not in s:
            tps = TaskPeriodSchedule(title=label, date_create=it.date, period=tp)
            it.counter = TaskPeriodSchedule.objects.filter().count()
            tps.save()
        else:
            tps = TaskPeriodSchedule.objects.get(period=tp, date_create__year=it.date.year, date_create__month=it.date.month, date_create__day=it.date.day)
        
        it.schedule = tps
        it.save()
        s.add(date)

    tp.recount_all()
    

def migrate_data(apps, schema_editor):
    migrate_chedule("daily-automation", JobTemplate.DAILY)
    migrate_chedule("weekly-automation", JobTemplate.WEEKLY)


def unmigrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_data, unmigrate_data, atomic=False),
    ]

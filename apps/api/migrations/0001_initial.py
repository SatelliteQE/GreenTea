# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.core.utils.date_helpers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=32, null=True, blank=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True)),
                ('date_create', apps.core.utils.date_helpers.TZDateTimeField(default=apps.core.utils.date_helpers.currentDate)),
                ('duration', models.FloatField()),
                ('exitcode', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

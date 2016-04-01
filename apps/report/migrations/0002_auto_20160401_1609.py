# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_test_external_links'),
        ('taskomatic', '0003_auto_20160105_1528'),
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(default=0)),
                ('rate', models.FloatField(default=0)),
                ('count', models.IntegerField(default=0)),
                ('result', models.TextField(blank=True)),
                ('schedule', models.ForeignKey(to='taskomatic.TaskPeriodSchedule')),
                ('test', models.ForeignKey(to='core.Test')),
            ],
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['name']},
        ),
    ]

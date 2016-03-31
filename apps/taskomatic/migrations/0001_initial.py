# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('common', models.CharField(max_length=128)),
                ('common_params', models.TextField(
                    verbose_name='Parameters', blank=True)),
                ('status', models.IntegerField(default=0, choices=[
                 (0, b'Waiting'), (1, b'In progress'), (2, b'Done'), (3, b'Error')])),
                ('exit_result', models.TextField(
                    verbose_name='Result log', blank=True)),
                ('date_create', models.DateTimeField(
                    default=django.utils.timezone.now, verbose_name='Date of create')),
                ('date_run', models.DateTimeField(null=True,
                                                  verbose_name='Date of pick up', blank=True)),
                ('time_long', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='TaskPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('label', models.SlugField(unique=True, max_length=64)),
                ('common', models.CharField(max_length=128)),
                ('date_last', models.DateTimeField(null=True,
                                                   verbose_name='Date of last run', blank=True)),
                ('is_enable', models.BooleanField(default=False)),
                ('cron', models.CharField(default=b'*  *  *  *  *', max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='TaskPeriodSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('date_create', models.DateTimeField(
                    default=django.utils.timezone.now, verbose_name='Date of create')),
                ('counter', models.BigIntegerField(default=0)),
                ('period', models.ForeignKey(blank=True,
                                             to='taskomatic.TaskPeriod', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='period',
            field=models.ForeignKey(
                blank=True, to='taskomatic.TaskPeriod', null=True),
        ),
    ]

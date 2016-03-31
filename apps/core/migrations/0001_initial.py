# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import taggit.managers
from django.db import migrations, models

import apps.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('taskomatic', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arch',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(
                    default=b'unknow@redhat.com', max_length=254)),
                ('is_enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CheckProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('datestart', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('dateend', models.DateTimeField(null=True, blank=True)),
                ('totalsum', models.IntegerField()),
                ('actual', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Distro',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DistroTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    help_text=b'Only alias', max_length=255, blank=True)),
                ('family', models.CharField(max_length=255, null=True, blank=True)),
                ('variant', models.CharField(max_length=255, null=True, blank=True)),
                ('distroname', models.CharField(
                    help_text=b'If field is empty, then it will use latest compose.', max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ('name', 'distroname'),
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=126)),
                ('url', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('alert', models.SmallIntegerField(default=1, choices=[
                 (0, b'success'), (1, b'info'), (2, b'warning'), (3, b'danger')])),
                ('is_enabled', models.BooleanField(default=True)),
                ('datestart', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('dateend', models.DateTimeField(
                    default=django.utils.timezone.now, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Git',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, null=True, blank=True)),
                ('localurl', models.CharField(max_length=255)),
                ('url', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GroupOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('email_notification', models.BooleanField(default=True)),
                ('owners', models.ManyToManyField(to='core.Author', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GroupTaskTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('params', models.TextField(blank=True)),
                ('priority', models.SmallIntegerField(default=0)),
            ],
            options={
                'ordering': ('priority',),
            },
            bases=(apps.core.models.ObjParams, models.Model),
        ),
        migrations.CreateModel(
            name='GroupTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='GroupTestTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('params', models.TextField(blank=True)),
                ('priority', models.SmallIntegerField(default=0)),
                ('group', models.ForeignKey(
                    related_name='grouptests', to='core.GroupTemplate')),
            ],
            options={
                'ordering': ('priority',),
            },
            bases=(apps.core.models.ObjParams, models.Model),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(unique=True,
                                         max_length=12, verbose_name=b'Job ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_running', models.BooleanField(default=False)),
                ('is_finished', models.BooleanField(default=False)),
                ('schedule', models.ForeignKey(blank=True,
                                               to='taskomatic.TaskPeriodSchedule', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('whiteboard', models.CharField(unique=True, max_length=255)),
                ('is_enable', models.BooleanField(default=False)),
                ('event_finish', models.SmallIntegerField(default=0, choices=[
                 (0, b'return'), (1, b'return when ok'), (2, b'reserve system')])),
                ('period', models.SmallIntegerField(
                    default=0, choices=[(0, b'daily'), (1, b'weekly')])),
                ('position', models.SmallIntegerField(default=0)),
                ('grouprecipes', models.CharField(
                    help_text=b'example: {{arch}} {{whiteboard|nostartsdate}}', max_length=255, blank=True)),
                ('schedule', models.ForeignKey(blank=True,
                                               to='taskomatic.TaskPeriod', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem',
                                                         blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ('period', 'position'),
            },
        ),
        migrations.CreateModel(
            name='PhaseLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PhaseResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('duration', models.FloatField()),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('phase', models.ForeignKey(to='core.PhaseLabel')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(unique=True,
                                         max_length=12, verbose_name=b'Recipe ID')),
                ('whiteboard', models.CharField(
                    max_length=64, verbose_name=b'Whiteboard')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, 'Unknow'), (7, 'New'), (8, 'Scheduled'), (1, 'Running'), (
                    2, 'Completed'), (3, 'Waiting'), (4, 'Queued'), (5, 'Aborted'), (6, 'Cancelled'), (9, 'Processed'), (10, 'Reserved')])),
                ('result', models.SmallIntegerField(default=0, choices=[(0, b'unknow'), (1, b'aborted'), (7, b'cancelled'), (2, b'waiting'), (
                    8, b'scheduled'), (6, b'new'), (3, b'warn'), (3, b'warning'), (4, b'fail'), (5, b'pass'), (9, b'panic'), (10, b'failinstall')])),
                ('resultrate', models.FloatField(default=-1.0)),
                ('statusbyuser', models.SmallIntegerField(
                    default=0, choices=[(0, 'none'), (11, 'waived')])),
                ('arch', models.ForeignKey(to='core.Arch')),
                ('distro', models.ForeignKey(to='core.Distro')),
                ('job', models.ForeignKey(related_name='recipes', to='core.Job')),
                ('parentrecipe', models.ForeignKey(
                    blank=True, to='core.Recipe', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('kernel_options', models.CharField(max_length=255, blank=True)),
                ('kernel_options_post', models.CharField(
                    max_length=255, blank=True)),
                ('ks_meta', models.CharField(max_length=255, blank=True)),
                ('role', models.SmallIntegerField(default=0, choices=[
                 (0, b'None'), (1, b'RECIPE_MEMBERS'), (2, b'STANDALONE')])),
                ('memory', models.CharField(max_length=255, blank=True)),
                ('disk', models.CharField(
                    help_text=b'Value is in GB', max_length=255, blank=True)),
                ('hvm', models.BooleanField(default=False)),
                ('params', models.TextField(blank=True)),
                ('is_virtualguest', models.BooleanField(default=False)),
                ('schedule', models.CharField(max_length=255,
                                              verbose_name=b'schedule period', blank=True)),
                ('arch', models.ManyToManyField(to='core.Arch')),
                ('distro', models.ForeignKey(to='core.DistroTemplate')),
                ('jobtemplate', models.ForeignKey(
                    related_name='trecipes', to='core.JobTemplate')),
                ('virtualhost', models.ForeignKey(related_name='virtualguests',
                                                  blank=True, to='core.RecipeTemplate', null=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model, apps.core.models.ObjParams),
        ),
        migrations.CreateModel(
            name='SkippedPhase',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('id_task', models.IntegerField()),
                ('id_phase', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(max_length=255, blank=True)),
                ('ram', models.IntegerField(null=True, blank=True)),
                ('cpu', models.CharField(max_length=255, blank=True)),
                ('hdd', models.CharField(max_length=255, blank=True)),
                ('group', models.SmallIntegerField(null=True, blank=True)),
                ('parent', models.ForeignKey(blank=True, to='core.System', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(unique=True,
                                         max_length=12, verbose_name=b'Task ID')),
                ('result', models.SmallIntegerField(default=0, choices=[(0, b'unknow'), (1, b'aborted'), (7, b'cancelled'), (2, b'waiting'), (
                    8, b'scheduled'), (6, b'new'), (3, b'warn'), (3, b'warning'), (4, b'fail'), (5, b'pass'), (9, b'panic'), (10, b'failinstall')])),
                ('status', models.SmallIntegerField(default=0, choices=[(0, 'Unknow'), (7, 'New'), (8, 'Scheduled'), (1, 'Running'), (
                    2, 'Completed'), (3, 'Waiting'), (4, 'Queued'), (5, 'Aborted'), (6, 'Cancelled'), (9, 'Processed'), (10, 'Reserved')])),
                ('duration', models.FloatField(default=-1.0)),
                ('datestart', models.DateTimeField(null=True, blank=True)),
                ('statusbyuser', models.SmallIntegerField(
                    default=0, choices=[(0, 'none'), (11, 'waived')])),
                ('alias', models.CharField(max_length=32, null=True, blank=True)),
                ('recipe', models.ForeignKey(to='core.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='TaskRoleEnum',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TaskTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('params', models.TextField(blank=True)),
                ('priority', models.SmallIntegerField(default=0)),
                ('recipe', models.ForeignKey(
                    related_name='tasks', to='core.RecipeTemplate')),
                ('role', models.ForeignKey(blank=True,
                                           to='core.TaskRoleEnum', null=True)),
            ],
            bases=(apps.core.models.ObjParams, models.Model),
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('time', models.CharField(max_length=6, null=True, blank=True)),
                ('type', models.CharField(max_length=32, null=True, blank=True)),
                ('folder', models.CharField(max_length=256, null=True, blank=True)),
                ('is_enable', models.BooleanField(
                    default=True, verbose_name=b'enable')),
                ('dependencies', models.ManyToManyField(
                    to='core.Test', blank=True)),
                ('git', models.ForeignKey(blank=True, to='core.Git', null=True)),
                ('groups', models.ManyToManyField(
                    to='core.GroupOwner', blank=True)),
                ('owner', models.ForeignKey(to='core.Author', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TestHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=24, null=True)),
                ('date', models.DateTimeField()),
                ('commit', models.CharField(max_length=64, null=True)),
                ('author', models.ForeignKey(to='core.Author', null=True)),
                ('test', models.ForeignKey(to='core.Test')),
            ],
        ),
        migrations.AddField(
            model_name='tasktemplate',
            name='test',
            field=models.ForeignKey(to='core.Test'),
        ),
        migrations.AddField(
            model_name='task',
            name='test',
            field=models.ForeignKey(to='core.Test'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='system',
            field=models.ForeignKey(to='core.System'),
        ),
        migrations.AddField(
            model_name='phaseresult',
            name='task',
            field=models.ForeignKey(to='core.Task'),
        ),
        migrations.AddField(
            model_name='job',
            name='template',
            field=models.ForeignKey(to='core.JobTemplate'),
        ),
        migrations.AddField(
            model_name='grouptesttemplate',
            name='role',
            field=models.ForeignKey(
                blank=True, to='core.TaskRoleEnum', null=True),
        ),
        migrations.AddField(
            model_name='grouptesttemplate',
            name='test',
            field=models.ForeignKey(to='core.Test'),
        ),
        migrations.AddField(
            model_name='grouptasktemplate',
            name='group',
            field=models.ForeignKey(
                related_name='grouptasks', to='core.GroupTemplate'),
        ),
        migrations.AddField(
            model_name='grouptasktemplate',
            name='recipe',
            field=models.ForeignKey(
                related_name='grouptemplates', to='core.RecipeTemplate'),
        ),
        migrations.AddField(
            model_name='grouptasktemplate',
            name='role',
            field=models.ForeignKey(
                blank=True, to='core.TaskRoleEnum', null=True),
        ),
    ]

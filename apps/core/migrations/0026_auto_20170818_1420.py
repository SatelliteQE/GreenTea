# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20170329_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('package', models.CharField(max_length=256, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.IntegerField()),
                ('title', models.CharField(max_length=256)),
                ('status', models.CharField(max_length=16)),
            ],
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'ordering': ('name', 'url'), 'verbose_name': 'repository', 'verbose_name_plural': 'repositories'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='result',
            field=models.SmallIntegerField(default=0, choices=[(0, b'unknow'), (1, b'aborted'), (2, b'waiting'), (3, b'warning'), (4, b'fail'), (5, b'pass'), (6, b'new'), (7, b'cancelled'), (8, b'scheduled'), (9, b'panic'), (10, b'failinstall'), (11, b'skip')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='result',
            field=models.SmallIntegerField(default=0, choices=[(0, b'unknow'), (1, b'aborted'), (7, b'cancelled'), (2, b'waiting'), (8, b'scheduled'), (6, b'new'), (3, b'warn'), (3, b'warning'), (4, b'fail'), (5, b'pass'), (9, b'panic'), (10, b'failinstall'), (11, b'skip')]),
        ),
        migrations.AddField(
            model_name='test',
            name='apps',
            field=models.ManyToManyField(to='core.AppTag', blank=True),
        ),
        migrations.AddField(
            model_name='test',
            name='bugs',
            field=models.ManyToManyField(to='core.Bug', blank=True),
        ),
    ]

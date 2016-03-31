# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=32)),
                ('content', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('action', models.SmallIntegerField(default=0, choices=[
                 (0, b'just comment'), (1, b'mark waived'), (2, b'return2beaker'), (3, b'reshedule job')])),
                ('job', models.ForeignKey(blank=True, to='core.Job', null=True)),
                ('recipe', models.ForeignKey(blank=True, to='core.Recipe', null=True)),
                ('task', models.ForeignKey(blank=True, to='core.Task', null=True)),
            ],
        ),
    ]

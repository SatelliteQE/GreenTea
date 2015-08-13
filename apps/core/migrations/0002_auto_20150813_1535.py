# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='url',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='checkprogress',
            name='datestart',
            field=models.DateTimeField(
                default=datetime.datetime(
                    2015,
                    8,
                    13,
                    13,
                    35,
                    48,
                    89008,
                    tzinfo=utc)),
            preserve_default=True,
        ),
    ]

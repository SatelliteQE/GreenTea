# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160316_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='filelog',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(
                2016, 3, 17, 15, 26, 40, 221466, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='filelog',
            name='path',
            field=models.CharField(unique=True, max_length=256),
        ),
    ]

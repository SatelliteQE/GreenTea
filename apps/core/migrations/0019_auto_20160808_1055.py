# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20160615_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Unknow'), (7, 'New'), (8, 'Scheduled'), (1, 'Running'), (2, 'Completed'), (3, 'Waiting'), (4, 'Queued'), (5, 'Aborted'), (6, 'Cancelled'), (9, 'Processed'), (10, 'Reserved'), (11, 'Installing')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Unknow'), (7, 'New'), (8, 'Scheduled'), (1, 'Running'), (2, 'Completed'), (3, 'Waiting'), (4, 'Queued'), (5, 'Aborted'), (6, 'Cancelled'), (9, 'Processed'), (10, 'Reserved'), (11, 'Installing')]),
        ),
    ]

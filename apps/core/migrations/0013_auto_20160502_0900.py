# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20160421_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filelog',
            name='task',
            field=models.ForeignKey(
                related_name='logfiles',
                blank=True,
                to='core.Task',
                null=True),
        ),
    ]

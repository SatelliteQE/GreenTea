# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_filelog_status_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='whiteboard',
            field=models.CharField(max_length=64, null=True, verbose_name=b'Whiteboard', blank=True),
        ),
    ]

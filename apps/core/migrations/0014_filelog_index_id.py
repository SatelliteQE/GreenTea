# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20160502_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='filelog',
            name='index_id',
            field=models.CharField(max_length=126, null=True, blank=True),
        ),
    ]

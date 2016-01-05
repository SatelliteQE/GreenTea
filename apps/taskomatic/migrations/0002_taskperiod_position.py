# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskomatic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskperiod',
            name='position',
            field=models.SmallIntegerField(default=0),
        ),
    ]

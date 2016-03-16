# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskomatic', '0002_taskperiod_position'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskperiod',
            options={'ordering': ['position', 'title']},
        ),
    ]

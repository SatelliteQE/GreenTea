# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskomatic', '0003_auto_20160105_1528'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskperiodschedule',
            options={'ordering': ['period_id', 'counter']},
        ),
    ]

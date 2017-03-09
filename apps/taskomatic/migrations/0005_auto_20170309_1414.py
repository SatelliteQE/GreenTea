# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskomatic', '0004_auto_20160627_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskperiod',
            name='common',
            field=models.CharField(help_text=b'All allowed <a href="https://github.com/SatelliteQE/GreenTea/wiki/Commands">commands</a>. Example: \'beaker schedule --schedule-label daily\'', max_length=128, verbose_name='Command'),
        ),
        migrations.AlterField(
            model_name='taskperiod',
            name='label',
            field=models.SlugField(help_text=b"Label must be same for command 'schedule --schedule-label [label]'", unique=True, max_length=64),
        ),
    ]

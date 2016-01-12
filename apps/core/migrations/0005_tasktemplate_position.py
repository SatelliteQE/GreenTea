# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20160105_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasktemplate',
            name='position',
            field=models.SmallIntegerField(default=2, choices=[(0, b'Begin'), (1, b'Pre group'), (2, b'Post group'), (3, b'End')]),
        ),
    ]

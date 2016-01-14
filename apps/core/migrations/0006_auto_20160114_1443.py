# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_tasktemplate_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasktemplate',
            name='position',
            field=models.SmallIntegerField(default=2, choices=[(0, b'Begin'), (1, b'Pre'), (2, b'Post'), (3, b'End')]),
        ),
    ]

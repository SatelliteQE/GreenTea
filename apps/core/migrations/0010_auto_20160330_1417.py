# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20160317_1626'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='test',
            options={'ordering': ['-is_enable', 'name']},
        ),
        migrations.AlterField(
            model_name='filelog',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

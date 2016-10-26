# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20161007_1220'),
        ('waiver', '0002_auto_20160421_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='test',
            field=models.ForeignKey(blank=True, to='core.Test', null=True),
        ),
    ]

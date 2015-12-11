# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150914_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(default=b'Unknown', max_length=255),
        ),
        migrations.AlterField(
            model_name='test',
            name='owner',
            field=models.ForeignKey(blank=True, to='core.Author', null=True),
        ),
    ]

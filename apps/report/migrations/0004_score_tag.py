# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('report', '0003_externalpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='tag',
            field=models.ForeignKey(blank=True, to='taggit.Tag', null=True),
        ),
    ]

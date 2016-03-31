# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20160330_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='external_links',
            field=models.TextField(
                help_text=b"external links which separated by ';'", null=True, blank=True),
        ),
    ]

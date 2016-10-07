# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160808_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipetemplate',
            name='params',
            field=models.TextField(verbose_name='extra XML parameter', blank=True),
        ),
        migrations.AlterField(
            model_name='recipetemplate',
            name='schedule',
            field=models.CharField(help_text=b'For example: s390x: 0,2,4; x86_64: 1,3,5,6', max_length=255, verbose_name='Schedule period', blank=True),
        ),
    ]

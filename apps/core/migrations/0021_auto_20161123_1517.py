# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20161007_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipetemplate',
            name='packages',
            field=models.CharField(default='', max_length=256, verbose_name='Extra packages'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipetemplate',
            name='params',
            field=models.TextField(verbose_name='Extra XML parameter', blank=True),
        ),
    ]

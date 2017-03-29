# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20170309_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='git',
            name='path',
            field=models.CharField(blank=True, max_length=255, null=True, help_text=b'Only local directory file:///mnt/git/..', validators=[apps.core.validators.validator_dir_exists]),
        ),
        migrations.AlterField(
            model_name='jobtemplate',
            name='grouprecipes',
            field=models.CharField(default=b'{{ whiteboard }}', help_text=b'example: {{arch}} {{whiteboard|nostartsdate}}', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='whiteboard',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Whiteboard', blank=True),
        ),
    ]

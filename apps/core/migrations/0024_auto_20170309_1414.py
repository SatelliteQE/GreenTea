# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20170214_1455'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='checkprogress',
            options={'verbose_name': 'Check progress', 'verbose_name_plural': 'Check progress'},
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'verbose_name': 'repository', 'verbose_name_plural': 'repositories'},
        ),
        migrations.AddField(
            model_name='git',
            name='path',
            field=models.CharField(blank=True, max_length=255, null=True, help_text=b'Possible only local file:///mnt...', validators=[apps.core.validators.validator_dir_exists]),
        ),
        migrations.AlterField(
            model_name='filelog',
            name='path',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]

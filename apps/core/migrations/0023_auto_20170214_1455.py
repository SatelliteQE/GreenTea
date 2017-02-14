# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20170109_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipetemplate',
            name='external_repos',
            field=models.ManyToManyField(to='core.Repository', blank=True),
        ),
        migrations.AlterField(
            model_name='repository',
            name='url',
            field=models.URLField(unique=True),
        ),
    ]

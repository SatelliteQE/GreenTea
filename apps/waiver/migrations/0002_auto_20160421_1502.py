# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waiver', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='recipe',
            field=models.ForeignKey(related_name='comments', blank=True, to='core.Recipe', null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='task',
            field=models.ForeignKey(related_name='comments', blank=True, to='core.Task', null=True),
        ),
    ]

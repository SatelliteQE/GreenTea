# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_test_external_links'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='recipe',
            field=models.ForeignKey(related_name='tasks', to='core.Recipe'),
        ),
    ]

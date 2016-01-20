# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20160114_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipetemplate',
            name='hostname',
            field=models.CharField(help_text=b"Set to '= system42.beaker.example.com' if you want your recipe to run on exactly this system", max_length=255, blank=True),
        ),
    ]

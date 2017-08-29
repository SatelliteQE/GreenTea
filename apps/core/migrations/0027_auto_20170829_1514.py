# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20170818_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bug',
            options={'ordering': ('uid',)},
        ),
        migrations.AddField(
            model_name='recipetemplate',
            name='labcontroller',
            field=models.CharField(help_text=b'= hostname.lab.example.com', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='apps',
            field=models.ManyToManyField(related_name='tests', to='core.AppTag', blank=True),
        ),
    ]

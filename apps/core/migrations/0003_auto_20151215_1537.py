# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150914_1800'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobtemplate',
            options={'ordering': ('schedule', 'position')},
        ),
        migrations.RemoveField(
            model_name='jobtemplate',
            name='period',
        ),
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(default=b'Unknown', max_length=255),
        ),
        migrations.AlterField(
            model_name='recipetemplate',
            name='hvm',
            field=models.BooleanField(default=False, verbose_name='Support virtualizaion'),
        ),
        migrations.AlterField(
            model_name='recipetemplate',
            name='params',
            field=models.TextField(verbose_name='Parameters', blank=True),
        ),
        migrations.AlterField(
            model_name='recipetemplate',
            name='schedule',
            field=models.CharField(max_length=255, verbose_name='Schedule period', blank=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='owner',
            field=models.ForeignKey(blank=True, to='core.Author', null=True),
        ),
    ]

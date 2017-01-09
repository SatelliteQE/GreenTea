# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20161123_1517'),
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('url', models.SlugField(max_length=1024, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='recipetemplate',
            name='packages',
            field=models.CharField(help_text=b'Separate by white space. For example: vim xen', max_length=256, verbose_name='Extra packages', blank=True),
        ),
        migrations.AddField(
            model_name='recipetemplate',
            name='external_repos',
            field=models.ManyToManyField(to='core.Repository'),
        ),
    ]

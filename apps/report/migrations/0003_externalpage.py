# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_auto_20160401_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('url', models.CharField(max_length=256)),
                ('is_enabled', models.BooleanField(default=True)),
            ],
        ),
    ]

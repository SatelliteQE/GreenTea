# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_recipetemplate_hostname'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=256)),
                ('recipe', models.ForeignKey(to='core.Recipe')),
                ('task', models.ForeignKey(blank=True, to='core.Task', null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='testhistory',
            options={'verbose_name': 'history of test',
                     'verbose_name_plural': 'history of tests'},
        ),
    ]

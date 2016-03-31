# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151215_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='email',
            field=models.EmailField(
                default=b'unknow@redhat.com', max_length=254, db_index=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(
                default=b'Unknown', max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='date',
            field=models.DateTimeField(
                default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='system',
            name='hostname',
            field=models.CharField(db_index=True, max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='folder',
            field=models.CharField(
                db_index=True, max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='is_enable',
            field=models.BooleanField(
                default=True, db_index=True, verbose_name=b'enable'),
        ),
        migrations.AlterField(
            model_name='test',
            name='name',
            field=models.CharField(unique=True, max_length=255, db_index=True),
        ),
    ]

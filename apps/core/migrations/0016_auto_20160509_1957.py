# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Count


def removed_duplicated(apps, schema_editor):
    FileLog = apps.get_model("core", "FileLog")
    for obj in FileLog.objects.values('url').annotate(
            Count('id')).order_by().filter(id__count__gt=1):
        for removed_duplicated in FileLog.objects.filter(path=obj["url"])[1:]:
            removed_duplicated.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20160509_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filelog',
            name='is_downloaded',
            field=models.BooleanField(
                default=False, verbose_name='File is downlaod'),
        ),
        migrations.AlterField(
            model_name='filelog',
            name='is_indexed',
            field=models.BooleanField(
                default=False, verbose_name='File is indexed'),
        ),
        migrations.RunPython(removed_duplicated, removed_duplicated),
        migrations.AlterField(
            model_name='filelog',
            name='url',
            field=models.CharField(unique=True, max_length=256),
        ),
    ]

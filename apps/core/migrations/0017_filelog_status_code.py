# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def status_code(apps, schema_editor):
    FileLog = apps.get_model("core", "FileLog")
    for it in FileLog.objects.filter(is_downloaded=True):
        it.status_code = 200
        it.save()

def skip(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160509_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='filelog',
            name='status_code',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.RunPython(status_code, skip),
    ]

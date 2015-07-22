# -*- coding: utf-8 -*-
from django.db import models
from south.db import db
from south.utils import datetime_utils as datetime
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaskPeriod'
        db.create_table(u'taskomatic_taskperiod', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('common', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('date_last', self.gf('django.db.models.fields.DateTimeField')
             (null=True, blank=True)),
            ('is_enable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cron', self.gf('django.db.models.fields.CharField')
             (default='*  *  *  *  *', max_length=64)),
        ))
        db.send_create_signal(u'taskomatic', ['TaskPeriod'])

        # Changing field 'Task.date_run'
        db.alter_column(u'taskomatic_task', 'date_run', self.gf(
            'apps.core.utils.date_helpers.TZDateTimeField')(null=True))

        # Changing field 'Task.date_create'
        db.alter_column(u'taskomatic_task', 'date_create', self.gf(
            'apps.core.utils.date_helpers.TZDateTimeField')())

    def backwards(self, orm):
        # Deleting model 'TaskPeriod'
        db.delete_table(u'taskomatic_taskperiod')

        # Changing field 'Task.date_run'
        db.alter_column(u'taskomatic_task', 'date_run', self.gf(
            'django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Task.date_create'
        db.alter_column(u'taskomatic_task', 'date_create',
                        self.gf('django.db.models.fields.DateTimeField')())

    models = {
        u'taskomatic.task': {
            'Meta': {'object_name': 'Task'},
            'common': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'common_params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_create': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'default': 'datetime.datetime(2014, 7, 2, 0, 0)'}),
            'date_run': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'exit_result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'time_long': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'taskomatic.taskperiod': {
            'Meta': {'object_name': 'TaskPeriod'},
            'common': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cron': ('django.db.models.fields.CharField', [], {'default': "'*  *  *  *  *'", 'max_length': '64'}),
            'date_last': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['taskomatic']

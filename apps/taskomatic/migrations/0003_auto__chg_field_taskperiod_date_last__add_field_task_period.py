# -*- coding: utf-8 -*-
from django.db import models
from south.db import db
from south.utils import datetime_utils as datetime
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TaskPeriod.date_last'
        db.alter_column(u'taskomatic_taskperiod', 'date_last', self.gf(
            'apps.core.utils.date_helpers.TZDateTimeField')(null=True))
        # Adding field 'Task.period'
        db.add_column(u'taskomatic_task', 'period',
                      self.gf('django.db.models.fields.related.ForeignKey')(
                          to=orm[
                              'taskomatic.TaskPeriod'], null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):

        # Changing field 'TaskPeriod.date_last'
        db.alter_column(u'taskomatic_taskperiod', 'date_last', self.gf(
            'django.db.models.fields.DateTimeField')(null=True))
        # Deleting field 'Task.period'
        db.delete_column(u'taskomatic_task', 'period_id')

    models = {
        u'taskomatic.task': {
            'Meta': {'object_name': 'Task'},
            'common': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'common_params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_create': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_run': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'exit_result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['taskomatic.TaskPeriod']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'time_long': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'taskomatic.taskperiod': {
            'Meta': {'object_name': 'TaskPeriod'},
            'common': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cron': ('django.db.models.fields.CharField', [], {'default': "'*  *  *  *  *'", 'max_length': '64'}),
            'date_last': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['taskomatic']

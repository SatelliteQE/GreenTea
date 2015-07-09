# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaskPeriodSchedule'
        db.create_table(u'taskomatic_taskperiodschedule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')
             (to=orm['taskomatic.TaskPeriod'], null=True, blank=True)),
            ('date_create', self.gf('apps.core.utils.date_helpers.TZDateTimeField')
             (default=datetime.datetime.now)),
            ('counter', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal(u'taskomatic', ['TaskPeriodSchedule'])

        # Adding field 'TaskPeriod.label'
        db.add_column(u'taskomatic_taskperiod', 'label',
                      self.gf('django.db.models.fields.CharField')(
                          max_length=64, null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'TaskPeriodSchedule'
        db.delete_table(u'taskomatic_taskperiodschedule')

        # Deleting field 'TaskPeriod.label'
        db.delete_column(u'taskomatic_taskperiod', 'label')

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
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'taskomatic.taskperiodschedule': {
            'Meta': {'object_name': 'TaskPeriodSchedule'},
            'counter': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'date_create': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['taskomatic.TaskPeriod']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['taskomatic']

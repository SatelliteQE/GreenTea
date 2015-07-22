# -*- coding: utf-8 -*-
from django.db import models
from south.db import db
from south.utils import datetime_utils as datetime
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Task'
        db.create_table(u'taskomatic_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('common', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('common_params', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('exit_result', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_create', self.gf('django.db.models.fields.DateTimeField')
             (default=datetime.datetime(2014, 1, 24, 0, 0))),
            ('date_run', self.gf('django.db.models.fields.DateTimeField')
             (null=True, blank=True)),
            ('time_long', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal(u'taskomatic', ['Task'])

    def backwards(self, orm):
        # Deleting model 'Task'
        db.delete_table(u'taskomatic_task')

    models = {
        u'taskomatic.task': {
            'Meta': {'object_name': 'Task'},
            'common': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'common_params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 24, 0, 0)'}),
            'date_run': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'exit_result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'time_long': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['taskomatic']

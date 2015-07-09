# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Performance'
        db.create_table(u'api_performance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_create', self.gf('apps.core.utils.date_helpers.TZDateTimeField')
             (default=datetime.datetime(2014, 11, 14, 0, 0))),
            ('duration', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'api', ['Performance'])

    def backwards(self, orm):
        # Deleting model 'Performance'
        db.delete_table(u'api_performance')

    models = {
        u'api.performance': {
            'Meta': {'object_name': 'Performance'},
            'date_create': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'default': 'datetime.datetime(2014, 11, 14, 0, 0)'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['api']

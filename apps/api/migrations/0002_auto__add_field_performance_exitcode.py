# -*- coding: utf-8 -*-
from django.db import models
from south.db import db
from south.utils import datetime_utils as datetime
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Performance.exitcode'
        db.add_column(u'api_performance', 'exitcode',
                      self.gf('django.db.models.fields.IntegerField')(
                          default=0),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Performance.exitcode'
        db.delete_column(u'api_performance', 'exitcode')

    models = {
        u'api.performance': {
            'Meta': {'object_name': 'Performance'},
            'date_create': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'default': 'datetime.datetime(2014, 11, 14, 0, 0)'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            'exitcode': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['api']

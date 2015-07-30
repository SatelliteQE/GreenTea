# -*- coding: utf-8 -*-
from django.db import models
from south.db import db
from south.utils import datetime_utils as datetime
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'JobTemplate.schedule'
        db.add_column(u'core_jobtemplate', 'schedule',
                      self.gf('django.db.models.fields.related.ForeignKey')(
                          to=orm[
                              'taskomatic.TaskPeriod'], null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'JobTemplate.schedule'
        db.delete_column(u'core_jobtemplate', 'schedule_id')

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.arch': {
            'Meta': {'object_name': 'Arch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'core.author': {
            'Meta': {'object_name': 'Author'},
            'email': ('django.db.models.fields.EmailField', [], {'default': "'unknow@redhat.com'", 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.checkprogress': {
            'Meta': {'object_name': 'CheckProgress'},
            'actual': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'dateend': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'datestart': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 7, 29, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'totalsum': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.distro': {
            'Meta': {'object_name': 'Distro'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'core.distrotemplate': {
            'Meta': {'ordering': "('name', 'distroname')", 'object_name': 'DistroTemplate'},
            'distroname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'family': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'variant': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.git': {
            'Meta': {'object_name': 'Git'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localurl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'core.groupowner': {
            'Meta': {'ordering': "['name']", 'object_name': 'GroupOwner'},
            'email_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Author']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'core.grouptasktemplate': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'GroupTaskTemplate'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'grouptasks'", 'to': u"orm['core.GroupTemplate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'grouptemplates'", 'to': u"orm['core.RecipeTemplate']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.TaskRoleEnum']", 'null': 'True', 'blank': 'True'})
        },
        u'core.grouptemplate': {
            'Meta': {'ordering': "('name',)", 'object_name': 'GroupTemplate'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'core.grouptesttemplate': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'GroupTestTemplate'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'grouptests'", 'to': u"orm['core.GroupTemplate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.TaskRoleEnum']", 'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Test']"})
        },
        u'core.job': {
            'Meta': {'object_name': 'Job'},
            'date': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_running': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['taskomatic.TaskPeriodSchedule']", 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.JobTemplate']"}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'})
        },
        u'core.jobtemplate': {
            'Meta': {'ordering': "('period', 'position')", 'object_name': 'JobTemplate'},
            'event_finish': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'grouprecipes': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['taskomatic.TaskPeriod']", 'null': 'True', 'blank': 'True'}),
            'whiteboard': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'core.phaselabel': {
            'Meta': {'object_name': 'PhaseLabel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'core.phaseresult': {
            'Meta': {'object_name': 'PhaseResult'},
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.PhaseLabel']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Task']"})
        },
        u'core.recipe': {
            'Meta': {'object_name': 'Recipe'},
            'arch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Arch']"}),
            'distro': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Distro']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipes'", 'to': u"orm['core.Job']"}),
            'parentrecipe': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Recipe']", 'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'resultrate': ('django.db.models.fields.FloatField', [], {'default': '-1.0'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'statusbyuser': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.System']"}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'}),
            'whiteboard': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'core.recipetemplate': {
            'Meta': {'ordering': "('name',)", 'object_name': 'RecipeTemplate'},
            'arch': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Arch']", 'symmetrical': 'False'}),
            'disk': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'distro': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.DistroTemplate']"}),
            'hvm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_virtualguest': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jobtemplate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trecipes'", 'to': u"orm['core.JobTemplate']"}),
            'kernel_options': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'kernel_options_post': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ks_meta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'memory': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'role': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'schedule': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'virtualhost': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'virtualguests'", 'null': 'True', 'to': u"orm['core.RecipeTemplate']"})
        },
        u'core.skippedphase': {
            'Meta': {'object_name': 'SkippedPhase'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_phase': ('django.db.models.fields.IntegerField', [], {}),
            'id_task': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.system': {
            'Meta': {'object_name': 'System'},
            'cpu': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hdd': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.System']", 'null': 'True', 'blank': 'True'}),
            'ram': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.task': {
            'Meta': {'object_name': 'Task'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'datestart': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '-1.0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Recipe']"}),
            'result': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'statusbyuser': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Test']"}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'})
        },
        u'core.taskroleenum': {
            'Meta': {'ordering': "('name',)", 'object_name': 'TaskRoleEnum'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'core.tasktemplate': {
            'Meta': {'object_name': 'TaskTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': u"orm['core.RecipeTemplate']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.TaskRoleEnum']", 'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Test']"})
        },
        u'core.test': {
            'Meta': {'ordering': "['name']", 'object_name': 'Test'},
            'dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Test']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'git': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Git']", 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.GroupOwner']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Author']", 'null': 'True'}),
            'time': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        u'core.testhistory': {
            'Meta': {'object_name': 'TestHistory'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Author']", 'null': 'True'}),
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'date': ('apps.core.utils.date_helpers.TZDateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Test']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        },
        u'taskomatic.taskperiod': {
            'Meta': {'object_name': 'TaskPeriod'},
            'common': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cron': ('django.db.models.fields.CharField', [], {'default': "'*  *  *  *  *'", 'max_length': '64'}),
            'date_last': ('apps.core.utils.date_helpers.TZDateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
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

    complete_apps = ['core']

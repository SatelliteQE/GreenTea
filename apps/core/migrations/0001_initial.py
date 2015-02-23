# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Arch'
        db.create_table(u'core_arch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal(u'core', ['Arch'])

        # Adding model 'Distro'
        db.create_table(u'core_distro', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'core', ['Distro'])

        # Adding model 'Git'
        db.create_table(u'core_git', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('localurl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'core', ['Git'])

        # Adding model 'Author'
        db.create_table(u'core_author', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(default='unknow@redhat.com', max_length=75)),
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'core', ['Author'])

        # Adding model 'Test'
        db.create_table(u'core_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('git', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Git'], null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Author'], null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('folder', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('is_enable', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'core', ['Test'])

        # Adding M2M table for field dependencies on 'Test'
        m2m_table_name = db.shorten_name(u'core_test_dependencies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_test', models.ForeignKey(orm[u'core.test'], null=False)),
            ('to_test', models.ForeignKey(orm[u'core.test'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_test_id', 'to_test_id'])

        # Adding model 'TestHistory'
        db.create_table(u'core_testhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Test'])),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=24, null=True)),
            ('date', self.gf('apps.core.utils.date_helpers.TZDateTimeField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Author'], null=True)),
            ('commit', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
        ))
        db.send_create_signal(u'core', ['TestHistory'])

        # Adding model 'System'
        db.create_table(u'core_system', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('ram', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cpu', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('hdd', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.System'], null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['System'])

        # Adding model 'JobTemplate'
        db.create_table(u'core_jobtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('whiteboard', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('is_enable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('event_finish', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('period', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('position', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('grouprecipes', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'core', ['JobTemplate'])

        # Adding model 'DistroTemplate'
        db.create_table(u'core_distrotemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('family', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('variant', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('distroname', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['DistroTemplate'])

        # Adding model 'RecipeTemplate'
        db.create_table(u'core_recipetemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('jobtemplate', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trecipes', to=orm['core.JobTemplate'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('kernel_options', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('kernel_options_post', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('ks_meta', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('role', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('memory', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('disk', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('hvm', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('params', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('distro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DistroTemplate'])),
            ('is_virtualguest', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('virtualhost', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='virtualguests', null=True, to=orm['core.RecipeTemplate'])),
            ('schedule', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'core', ['RecipeTemplate'])

        # Adding M2M table for field arch on 'RecipeTemplate'
        m2m_table_name = db.shorten_name(u'core_recipetemplate_arch')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recipetemplate', models.ForeignKey(orm[u'core.recipetemplate'], null=False)),
            ('arch', models.ForeignKey(orm[u'core.arch'], null=False))
        ))
        db.create_unique(m2m_table_name, ['recipetemplate_id', 'arch_id'])

        # Adding model 'TaskRoleEnum'
        db.create_table(u'core_taskroleenum', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'core', ['TaskRoleEnum'])

        # Adding model 'GroupTemplate'
        db.create_table(u'core_grouptemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['GroupTemplate'])

        # Adding model 'GroupTaskTemplate'
        db.create_table(u'core_grouptasktemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='grouptasks', to=orm['core.GroupTemplate'])),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(related_name='grouptemplates', to=orm['core.RecipeTemplate'])),
            ('params', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('priority', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TaskRoleEnum'], null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['GroupTaskTemplate'])

        # Adding model 'GroupTestTemplate'
        db.create_table(u'core_grouptesttemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Test'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='grouptests', to=orm['core.GroupTemplate'])),
            ('params', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('priority', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TaskRoleEnum'], null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['GroupTestTemplate'])

        # Adding model 'TaskTemplate'
        db.create_table(u'core_tasktemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Test'])),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['core.RecipeTemplate'])),
            ('params', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('priority', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TaskRoleEnum'], null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['TaskTemplate'])

        # Adding model 'Job'
        db.create_table(u'core_job', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.JobTemplate'])),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=12)),
            ('date', self.gf('apps.core.utils.date_helpers.TZDateTimeField')(default=datetime.datetime.now)),
            ('is_running', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['Job'])

        # Adding model 'Recipe'
        db.create_table(u'core_recipe', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipes', to=orm['core.Job'])),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=12)),
            ('whiteboard', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('result', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('resultrate', self.gf('django.db.models.fields.FloatField')(default=-1.0)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.System'])),
            ('arch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Arch'])),
            ('distro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Distro'])),
            ('parentrecipe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Recipe'], null=True, blank=True)),
            ('statusbyuser', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['Recipe'])

        # Adding model 'Task'
        db.create_table(u'core_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=12)),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Recipe'])),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Test'])),
            ('result', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('duration', self.gf('django.db.models.fields.FloatField')(default=-1.0)),
            ('datestart', self.gf('apps.core.utils.date_helpers.TZDateTimeField')(null=True, blank=True)),
            ('statusbyuser', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Task'])

        # Adding model 'PhaseLabel'
        db.create_table(u'core_phaselabel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'core', ['PhaseLabel'])

        # Adding model 'PhaseResult'
        db.create_table(u'core_phaseresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Task'])),
            ('phase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.PhaseLabel'])),
            ('duration', self.gf('django.db.models.fields.FloatField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['PhaseResult'])

        # Adding model 'SkippedPhase'
        db.create_table(u'core_skippedphase', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_task', self.gf('django.db.models.fields.IntegerField')()),
            ('id_phase', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'core', ['SkippedPhase'])

        # Adding model 'CheckProgress'
        db.create_table(u'core_checkprogress', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datestart', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 2, 3, 0, 0))),
            ('dateend', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('totalsum', self.gf('django.db.models.fields.IntegerField')()),
            ('actual', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['CheckProgress'])


    def backwards(self, orm):
        # Deleting model 'Arch'
        db.delete_table(u'core_arch')

        # Deleting model 'Distro'
        db.delete_table(u'core_distro')

        # Deleting model 'Git'
        db.delete_table(u'core_git')

        # Deleting model 'Author'
        db.delete_table(u'core_author')

        # Deleting model 'Test'
        db.delete_table(u'core_test')

        # Removing M2M table for field dependencies on 'Test'
        db.delete_table(db.shorten_name(u'core_test_dependencies'))

        # Deleting model 'TestHistory'
        db.delete_table(u'core_testhistory')

        # Deleting model 'System'
        db.delete_table(u'core_system')

        # Deleting model 'JobTemplate'
        db.delete_table(u'core_jobtemplate')

        # Deleting model 'DistroTemplate'
        db.delete_table(u'core_distrotemplate')

        # Deleting model 'RecipeTemplate'
        db.delete_table(u'core_recipetemplate')

        # Removing M2M table for field arch on 'RecipeTemplate'
        db.delete_table(db.shorten_name(u'core_recipetemplate_arch'))

        # Deleting model 'TaskRoleEnum'
        db.delete_table(u'core_taskroleenum')

        # Deleting model 'GroupTemplate'
        db.delete_table(u'core_grouptemplate')

        # Deleting model 'GroupTaskTemplate'
        db.delete_table(u'core_grouptasktemplate')

        # Deleting model 'GroupTestTemplate'
        db.delete_table(u'core_grouptesttemplate')

        # Deleting model 'TaskTemplate'
        db.delete_table(u'core_tasktemplate')

        # Deleting model 'Job'
        db.delete_table(u'core_job')

        # Deleting model 'Recipe'
        db.delete_table(u'core_recipe')

        # Deleting model 'Task'
        db.delete_table(u'core_task')

        # Deleting model 'PhaseLabel'
        db.delete_table(u'core_phaselabel')

        # Deleting model 'PhaseResult'
        db.delete_table(u'core_phaseresult')

        # Deleting model 'SkippedPhase'
        db.delete_table(u'core_skippedphase')

        # Deleting model 'CheckProgress'
        db.delete_table(u'core_checkprogress')


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
            'datestart': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 3, 0, 0)'}),
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
        u'core.grouptasktemplate': {
            'Meta': {'object_name': 'GroupTaskTemplate'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'grouptasks'", 'to': u"orm['core.GroupTemplate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'grouptemplates'", 'to': u"orm['core.RecipeTemplate']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.TaskRoleEnum']", 'null': 'True', 'blank': 'True'})
        },
        u'core.grouptemplate': {
            'Meta': {'object_name': 'GroupTemplate'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'core.grouptesttemplate': {
            'Meta': {'object_name': 'GroupTestTemplate'},
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
        }
    }

    complete_apps = ['core']
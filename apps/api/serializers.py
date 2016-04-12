

from rest_framework import serializers

from apps.core.models import Job, JobTemplate, Recipe, Task, Test, Author, \
    Arch, Distro, System
from apps.waiver.models import Comment


class ResultField(serializers.Field):
    def get_attribute(self, obj):
        return obj.get_result_display()

    def to_representation(self, obj):
        return obj


class StatusField(serializers.Field):
    def get_attribute(self, obj):
        return obj.get_status_display()

    def to_representation(self, obj):
        return obj


class StatusByUserField(serializers.Field):
    def get_attribute(self, obj):
        return obj.get_statusbyuser_display()

    def to_representation(self, obj):
        return None if obj == "none" else obj


class JobTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobTemplate
        fields = ('id', 'whiteboard', 'is_enable', 'position')


class ArchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arch


class DistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distro


class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe

    class InnerTaskSerializer(serializers.ModelSerializer):
        class Meta:
            model = Task
            fields = ('id', 'result', 'status', 'statusbyuser')

    job = JobSerializer()
    arch = ArchSerializer()
    distro = DistroSerializer()
    system = SystemSerializer()
    job_name = serializers.CharField(source='job.template.whiteboard',
                                     read_only=True)
    result = ResultField()
    status = StatusField()
    statusbyuser = StatusByUserField()
    comments = serializers.ManyRelatedField(child_relation=CommentSerializer())
    tasks = serializers.ManyRelatedField(child_relation=InnerTaskSerializer())


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task

    class InnerTestSerializer(serializers.ModelSerializer):
        class Meta:
            model = Test
            fields = ('id', 'name', 'owner')

    test = InnerTestSerializer()
    result = ResultField()
    status = StatusField()
    statusbyuser = StatusByUserField()
    comments = serializers.ManyRelatedField(child_relation=CommentSerializer())

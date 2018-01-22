

from rest_framework import serializers

from apps.core.models import (Arch, Author, Distro, Job, JobTemplate, Recipe,
                              System, Task, Test)
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
        fields = '__all__'


class DistroSerializer(serializers.ModelSerializer):

    class Meta:
        model = Distro
        fields = '__all__'


class SystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = System
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = '__all__'

    date = serializers.DateTimeField('%Y-%m-%d %X')


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'

    created_date = serializers.DateTimeField('%Y-%m-%d %X')


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = '__all__'

    repository_url = serializers.CharField(source='get_reposituory_url')
    detail_url = serializers.CharField(source='get_detail_url')
    external_links = serializers.CharField(source='get_external_links')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'

    class InnerTaskSerializer(serializers.ModelSerializer):

        class Meta:
            model = Task
            fields = ('id', 'result', 'status', 'statusbyuser', 'test_name',
                      'duration')
        test_name = serializers.CharField(source='test.name', read_only=True)

    job = JobSerializer()
    arch = ArchSerializer()
    distro = DistroSerializer()
    system = SystemSerializer()
    job_name = serializers.CharField(source='job.template.whiteboard',
                                     read_only=True)
    # result = ResultField()
    # status = StatusField()
    # statusbyuser = StatusByUserField()
    comments = serializers.SerializerMethodField('get_my_comments')
    tasks = serializers.SerializerMethodField('get_my_tasks')
    parent = serializers.SerializerMethodField('get_my_parent')

    def get_my_tasks(self, recipe):
        tasks_queryset = Task.objects\
                             .filter(recipe=recipe).order_by('id')\
                             .select_related('test')
        serializer = RecipeSerializer.InnerTaskSerializer(
            instance=tasks_queryset, many=True, context=self.context)
        return serializer.data

    def get_my_comments(self, recipe):
        comments_queryset = Comment.objects.all()\
                                   .filter(recipe=recipe, task__isnull=True)
        serializer = CommentSerializer(instance=comments_queryset, many=True,
                                       context=self.context)
        return serializer.data

    def get_my_parent(self, recipe):
        # This is WA, because parameter 'parentrecipe' is allways empty.
        o_job = recipe.job.get_original_job()
        if (o_job):
            o_recipe = Recipe.objects.filter(job=o_job,
                                             whiteboard=recipe.whiteboard)\
                .values('id')[:1]
            if (o_recipe):
                return o_recipe[0]
        return None


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'

    class InnerTestSerializer(serializers.ModelSerializer):

        class Meta:
            model = Test
            fields = ('id', 'name', 'owner', 'repository_url', 'detail_url',
                      'external_links')

        repository_url = serializers.CharField(source='get_reposituory_url')
        detail_url = serializers.CharField(source='get_detail_url')
        # external_links = serializers.StringRelatedField(source='get_external_links')

    class InnerRecipeSerializer(RecipeSerializer):

        class Meta:
            model = Recipe
            # fields = "__all__"
            fields = ("id", "job", "arch", "comments")
            # from rest framework 3.3 is not possible set exclude = ('tasks', )
            # exclude = ('tasks', )

    test = InnerTestSerializer()
    # result = ResultField()
    # status = StatusField()
    # statusbyuser = StatusByUserField()
    recipe = InnerRecipeSerializer()
    comments = serializers.ManyRelatedField(child_relation=CommentSerializer())
    logfiles = serializers.StringRelatedField(many=True)

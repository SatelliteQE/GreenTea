

from rest_framework import serializers

from apps.core.models import Job, JobTemplate, Recipe


class JobTemplateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = JobTemplate
        fields = ('id', 'whiteboard', 'is_enable', 'position')


class RecipeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'uid')
        write_only_fields = ()

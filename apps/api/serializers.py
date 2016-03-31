

from apps.core.models import JobTemplate, Recipe, Job
from rest_framework import serializers


class JobTemplateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = JobTemplate
        fields = ('id', 'whiteboard', 'is_enable', 'position')


class RecipeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'uid')
        write_only_fields = ()

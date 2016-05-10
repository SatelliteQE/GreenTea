#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from apps.core.models import JobTemplate, Recipe, \
    Task, Author, Arch, Distro, System, Test
from apps.waiver.models import Comment
from models import Performance
from filters import TaskFilter
from serializers import JobTemplateSerializer, RecipeSerializer, \
    TaskSerializer, AuthorSerializer, ArchSerializer, \
    DistroSerializer, SystemSerializer, \
    CommentSerializer, TestSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Recipe.objects.all().select_related('job', 'arch', 'distro')
    serializer_class = RecipeSerializer
    ordering_fields = '__all__'
    ordering = ('-uid',)
    filter_fields = ('uid', )
    http_method_names = ['get', 'head']


class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Author.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    ordering_fields = '__all__'
    ordering = ('-email',)
    http_method_names = ['get', 'head']


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Tasks. It is possible to use attribute 'results' for
    filtering more then one result.
    &results=3,4,5
    """
    queryset = Task.objects.all().select_related('test')
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    ordering_fields = '__all__'
    ordering = ('-uid',)
    http_method_names = ['get', 'head']


class JobTemplateViewSet(viewsets.ModelViewSet):
    queryset = JobTemplate.objects.all()
    serializer_class = JobTemplateSerializer
    ordering_fields = '__all__'
    ordering = ('-id',)
    filter_fields = ('uid', )
    http_method_names = ['get', 'head']


class ArchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Arch.
    """
    queryset = Arch.objects.all()
    serializer_class = ArchSerializer
    ordering_fields = '__all__'
    ordering = ('-id',)
    http_method_names = ['get', 'head']


class DistroViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Distro.
    """
    queryset = Distro.objects.all()
    serializer_class = DistroSerializer
    ordering_fields = '__all__'
    ordering = ('-id',)
    http_method_names = ['get', 'head']


class SystemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for System.
    """
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    ordering_fields = '__all__'
    ordering = ('-id',)
    http_method_names = ['get', 'head']


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    ordering_fields = '__all__'
    ordering = ('-id',)
    http_method_names = ['get', 'head']


class TestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Test.
    """
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    ordering_fields = '__all__'
    ordering = ('-id',)
    http_method_names = ['get', 'head']


@csrf_exempt
def performance(request):
    perf = Performance(
        label=request.POST.get("label"),
        name=request.POST.get("name"),
        description=request.POST.get("description"),
        exitcode=request.POST.get("exitcode", -1),
        duration=request.POST.get("duration")
    )
    perf.save()
    data = "ok"
    return HttpResponse(data, mimetype="application/json")

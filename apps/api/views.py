#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from models import Performance
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from serializers import RecipeSerializer, JobTemplateSerializer
from apps.core.models import Recipe, JobTemplate, Task
from apps.core.models import (FAIL, NEW, WAIVED, WARN)
from apps.waiver.models import Comment
from apps.core.views import base


class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Recipe.objects.all().order_by("-uid")
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'head']

    def retrieve(self, request, pk=None):
        recipe = Recipe.objects.get(uid=pk)
        tasks = Task.objects.filter(recipe=recipe).order_by('uid')

        data = {
            'results': recipe.get_result(),
            'recipe': recipe.to_json(),
            'job': recipe.job.to_json(),
            'job_name': recipe.job.template.whiteboard,
            'task_progress': [],
            'tasks': [],
        }

        # TODO rewrite this part code - looks crazy
        count = len(tasks)
        counter = 0
        ecount = 0
        commentsCounter = 0
        last_result = -10
        sum = 0
        for task in tasks:
            if task.result in [NEW, WARN, FAIL]:
                ecount += 1
                tComments = Comment.objects.filter(task=task, recipe=recipe)\
                                   .order_by('-created_date')
                if len(tComments) > 0:
                    commentsCounter += 1
                if ecount < 10:
                    tjson = task.to_json()
                    tjson['comments'] = [comm.to_json() for comm in tComments]
                    data['tasks'].append(tjson)
            tres = task.get_result_display()
            if task.statusbyuser == WAIVED:
                tres = task.get_statusbyuser_display()
            if tres != last_result:
                if last_result and counter > 0:
                    perc = max(counter * 100 / count, 1)
                    data['task_progress'].append((last_result,
                                                  perc, counter))
                    sum += perc
                counter = 0
            last_result = tres
            counter += 1
        perc = max(counter * 100 / count, 1)
        sum += perc
        if not recipe.job.is_running and sum < 100:
            perc += 100 - sum
        if sum > 100:
            perc -= (sum - 100)

        # TOOD doesnt work with schedule plan
        # data['reschduled'] = self.getReschdulesOfRecipe(recipe)
        data['reschduled'] = ()

        data['task_progress'].append((last_result, perc, counter))
        data['task_len'] = ecount
        data['comments_counter'] = commentsCounter

        comments = Comment.objects.filter(recipe=recipe, task__isnull=True)\
            .order_by('-created_date')
        data['comments'] = [comm.to_json() for comm in comments]

        return Response(data)


class JobTemplateViewSet(viewsets.ModelViewSet):
    queryset = JobTemplate.objects.all().order_by("-is_enable", "position")
    serializer_class = JobTemplateSerializer
    http_method_names = ['get', 'head']

    def retrieve(self, request, pk=None):
        jobtempalte = JobTemplate.objects.get(id=pk)
        data = {
            "title": jobtempalte.whiteboard,
            "is_enable": jobtempalte.is_enable,
            "url": jobtempalte.get_absolute_url(),
            "schedule": jobtempalte.schedule.label,
            "xml": base.get_xml(jobtempalte),

        }
        return Response(data)

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

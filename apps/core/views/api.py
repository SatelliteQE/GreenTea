# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import hashlib
import logging
import sys
from copy import copy
from datetime import datetime, timedelta

from django.conf import settings
from django.db import connection
from django.db.models import Count
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from taggit.models import Tag

from apps.core.forms import FilterForm
from apps.core.models import (RESULT_CHOICES, Author, CheckProgress, Event,
                              JobTemplate, Recipe, render_label)
from apps.taskomatic.models import TaskPeriodSchedule
from apps.waiver.forms import WaiverForm
from apps.waiver.models import Comment
from base import create_matrix

logger = logging.getLogger(__name__)


class ApiView(View):
    content_type = 'application/json'

    def getReschdulesOfRecipe(self, recipe):
        # Get all previous scheduled job of this job
        # TODO: predelat
        j_date = recipe.job.date
        date_range = (TZDatetime(*j_date.timetuple()[:3], hour=19, minute=0),
                      TZDatetime(*(j_date + timedelta(days=1))
                                 .timetuple()[:3], hour=18, minute=55))
        rescheduled = Job.objects.filter(template=recipe.job.template,
                                         date__range=date_range)\
            .exclude(id=recipe.job.id)
        return [job.to_json() for job in rescheduled]

    def getRecipeComments(self, recipe):
        rComments = Comment.objects.filter(recipe=recipe, task__isnull=True)\
            .order_by('-created_date')
        return [comm.to_json() for comm in rComments]

    def getRecipeInfo(self, params, content):
        uid = params.get("recipe")
        if uid.startswith("R:"):
            uid = uid[2:]
        try:
            recipe = Recipe.objects.get(uid=uid)
        except Recipe.DoesNotExist:
            raise Http404

        content['results'] = recipe.get_result()
        content['recipe'] = recipe.to_json()
        content['job'] = recipe.job.to_json()
        content['job_name'] = recipe.job.template.whiteboard
        f2_tasks = Task.objects.filter(recipe=recipe).order_by('uid')
        content['task_progress'] = list()
        content['tasks'] = list()
        count = len(f2_tasks)
        counter = 0
        ecount = 0
        commentsCounter = 0
        last_result = -10
        sum = 0
        for task in f2_tasks:
            if task.result in [NEW, WARN, FAIL]:
                ecount += 1
                tComments = Comment.objects.filter(task=task, recipe=recipe)\
                                   .order_by('-created_date')
                if len(tComments) > 0:
                    commentsCounter += 1
                if ecount < 10:
                    tjson = task.to_json()
                    tjson['comments'] = [comm.to_json() for comm in tComments]
                    content['tasks'].append(tjson)
            tres = task.get_result_display()
            if task.statusbyuser == WAIVED:
                tres = task.get_statusbyuser_display()
            if tres != last_result:
                if last_result and counter > 0:
                    perc = max(counter * 100 / count, 1)
                    content['task_progress'].append((last_result,
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
        content['task_progress'].append((last_result, perc, counter))
        content['task_len'] = ecount
        content['comments_counter'] = commentsCounter
        content['reschduled'] = self.getReschdulesOfRecipe(recipe)
        content['comments'] = self.getRecipeComments(recipe)

    def getRecipeTasks(self, params, content):
        uid = params.get("recipe")
        from_ix = int(params.get("from", 0))
        if uid.startswith("R:"):
            uid = uid[2:]
        try:
            recipe = Recipe.objects.get(uid=uid)
        except Recipe.DoesNotExist:
            raise Http404
        f_tasks = Task.objects.filter(recipe=recipe).order_by('uid')
        if params.get("filter", 'errors') == 'errors':
            f_tasks = f_tasks.filter(result__in=[NEW, WARN, FAIL])
        f_tasks.order_by('uid')
        content['task_len'] = len(f_tasks)
        content['tasks'] = list()
        for task in f_tasks[from_ix:from_ix + 10]:
            tjson = task.to_json()
            comments = Comment.objects.filter(task=task, recipe=recipe)
            tjson['comments'] = [comm.to_json() for comm in comments]
            content['tasks'].append(tjson)

    def getTaskInfo(self, params, content):
        uid = params.get("task")
        # from_ix = int(params.get("from", 0))
        if uid.startswith("T:"):
            uid = uid[2:]
        task = None
        try:
            task = Task.objects.get(uid=uid)
        except Recipe.DoesNotExist:
            raise Http404
        tComments = Comment.objects.filter(task=task).order_by('-created_date')
        content['task'] = task.to_json()
        content['task']['comments'] = [comm.to_json() for comm in tComments]
        content['results'] = task.get_result()
        recipe = task.recipe
        content['reschduled'] = self.getReschdulesOfRecipe(recipe)
        content['recipe'] = recipe.to_json()
        content['recipe']['comments'] = self.getRecipeComments(recipe)
        content['job'] = recipe.job.to_json()
        content['job_name'] = recipe.job.template.whiteboard

    def getOwnersList(self, params, content):
        owners = None
        key = params.get("key", False)
        if key:
            owners = Author.objects.filter(Q(name__contains=key) |
                                           Q(email__contains=key))
        else:
            owners = Author.objects.all()
        content['owners'] = [own.to_json() for own in owners] if owners else []

    def getGitChange(self, params, content):
        ids = params.get("ids", "").rstrip('|').split('|')
        test_history = TestHistory.objects.filter(id__in=ids).order_by('-date')
        content['changes'] = [change.to_json() for change in test_history]\
            if test_history else []

    def apiEvent(self, action, params):
        content = dict()
        if action == 'recipe-info':
            self.getRecipeInfo(params, content)
        elif action == 'recipe-tasks':
            self.getRecipeTasks(params, content)
        elif action == 'task-info':
            self.getTaskInfo(params, content)
        elif action == 'owners':
            self.getOwnersList(params, content)
        elif action == 'git-changes':
            self.getGitChange(params, content)
        return HttpResponse(json.dumps(content))

    def get(self, request, action, *args, **kwargs):
        return self.apiEvent(action, request.GET)

    def post(self, request, action, *args, **kwargs):
        return self.apiEvent(action, request.POST)


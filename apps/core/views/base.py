# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import json
import logging
from datetime import date, datetime, timedelta

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from apps.core.forms import GroupsForm, JobForm
from apps.core.models import (FAIL, NEW, WAIVED, WARN, Author, CheckProgress,
                              EnumResult, Job, JobTemplate, Recipe,
                              RecipeTemplate, Task, Test, TestHistory)
from apps.core.utils.beaker import JobGen
from apps.core.utils.beaker_import import Parser
from apps.core.utils.date_helpers import TZDatetime
from apps.taskomatic.models import TaskPeriodSchedule
from apps.waiver.models import Comment

logger = logging.getLogger(__name__)


@login_required
def import_xml(request):
    # TODO: rewrite to standard View Class
    data = {}
    if request.POST and "textxml" in request.POST:
        xml = request.POST["textxml"].strip()
        s = Parser(content=xml)
        if not s.status:
            data["error"] = s.error
        else:
            s.run()
            data["xml"] = xml
            data["job"] = s.job
            data["recipes"] = RecipeTemplate.objects.filter(jobtemplate=s.job)

    return render(request, 'import_xml.html', data)


def import_group(request):
    # TODO: rewrite to standard View Class
    data = {"forms": GroupsForm()}
    if request.POST and "group" in request.POST:
        forms = GroupsForm(request.POST)
        if forms.is_valid():
            data["group"] = forms.save()
        data["forms"] = forms
    return render(request, 'import_group.html', data)


def get_xml(jobT):
    """Takes JobTemplate object and returns its prettified job XML"""
    jobG = JobGen()
    xml = jobG.getXML(jobT, reserve=True)
    soup = BeautifulSoup(xml, "xml")
    return soup.prettify()


def to_xml(request, id):
    # TODO: rewrite to standard View Class
    try:
        jobT = JobTemplate.objects.get(id=id)
    except JobTemplate.DoesNotExist:
        raise Http404
    xml = get_xml(jobT)
    return render(request, 'job_xml.html',
                  {'template': jobT, "xml": xml, "beaker": settings.BEAKER_SERVER})


def create_matrix(days):
    datearray = []
    index = 0
    while True:
        index += 1
        newday = date.today() - timedelta(days=index)
        # suturday and sunday were ignored
        if newday.weekday() in (4, 5):
            continue
        datearray.append(newday)  # .strftime("%Y-%m-%d"))
        if len(datearray) == days:
            break
    return list(reversed(datearray))


def statistic(request):
    content = "TODO"
    # we need create statistic page
    return HttpResponse(content, content_type='text/plain')


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


class HomePageView(TemplateView):
    template_name = 'homepage.html'
    filters = {}
    forms = {}

    def get_network_stas(self, **kwargs):
        def get_lab(hostname, num):
            return ".".join(hostname.split(".")[-1 * num:])

        # TODO - show only some last runs
        start, end = 0, 7
        periods = TaskPeriodSchedule.objects.all().values(
            "title", "date_create", "id", "counter").order_by("title", "-date_create")
        ids = map(lambda x: x["id"], periods)

        tasks = Task.objects.filter(recipe__job__schedule_id__in=ids) \
            .values("result", "recipe__system__hostname", "recipe__job__schedule__id") \
            .annotate(results=Count("result"),
                      hosts=Count("recipe__system__hostname"),
                      label=Count("recipe__job__schedule")) \
            .order_by("recipe__system__hostname", "recipe__job__schedule__id")

        data = {}
        labels = set()
        ER = EnumResult()
        for it in tasks:
            hostname = get_lab(it.get("recipe__system__hostname"), 4)
            schedule = it.get("recipe__job__schedule__id")
            result, count = ER.get(it.get("result")), it.get("hosts")
            labels.add(schedule)
            if hostname in data:
                if schedule not in data[hostname]:
                    data[hostname].update({schedule: {result: count}})
                data[hostname][schedule][result] = count
            else:
                data[hostname] = {schedule: {result: count}}

        for hostname, value in data.items():
            for schedule in labels:
                if not value.get(schedule):
                    data[hostname][schedule] = {}
        return {"labels": labels, "data": data}

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        try:
            context['progress'] = CheckProgress.objects.order_by(
                "-datestart")[0]
        except IndexError:
            context['progress'] = None
        # Waiver
        comments = Comment.objects\
            .filter(created_date__gt=datetime.today().date())\
            .order_by("-created_date", "task", "recipe", "job")
        paginator = Paginator(comments, settings.PAGINATOR_OBJECTS_ONHOMEPAGE)
        context['waiver'] = paginator.page(
            int(self.request.GET.get('cpage', 1)))
        context['cpaginator'] = paginator
        history = TestHistory.objects.filter().order_by(
            "-date")[:settings.PAGINATOR_OBJECTS_ONHOMEPAGE * 10]
        paginator = Paginator(history, settings.PAGINATOR_OBJECTS_ONHOMEPAGE)
        context['history'] = paginator.page(
            int(self.request.GET.get('hpage', 1)))
        context['hpaginator'] = paginator

        context['networking'] = self.get_network_stas()
        return context


class JobDetailView(TemplateView):
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        job_id = kwargs["id"]
        oJobTmp = JobTemplate.objects.get(id=job_id)
        jobs_list = Job.objects.filter(template=oJobTmp).order_by("-date")

        paginator = Paginator(jobs_list, settings.PAGINATOR_OBJECTS_ONPAGE)
        jobs = paginator.page(int(self.request.GET.get('page', 1)))

        context.update({
            "jobtemplate": oJobTmp,
            "jobs": jobs,
            "paginator": paginator,
        })
        return context


class TestDetailView(TemplateView):
    template_name = 'test-detail.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        test_id = kwargs["id"]
        oTest = Test.objects.get(id=test_id)
        task_list = Task.objects.filter(
            test=oTest).order_by("-recipe__job__date")

        paginator = Paginator(task_list, settings.PAGINATOR_OBJECTS_ONPAGE)
        tasks = paginator.page(int(self.request.GET.get('page', 1)))

        context.update({
            "jobtemplate": oTest,
            "tasks": tasks,
            "paginator": paginator
        })
        return context


class JobsDiffView(TemplateView):
    template_name = 'diffs.html'

    def dispatch(self, request, *args, **kwargs):
        self.filters = {}
        self.forms = {}
        return super(JobsDiffView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        if 'jobs' in self.forms:
            context["form"] = self.forms['jobs']
        else:
            context["form"] = JobForm()
        return context

    def formEvent(self, parametrs):
        jobform = JobForm(parametrs)
        self.forms['jobs'] = jobform

    def post(self, request, *args, **kwargs):
        self.formEvent(request.POST)
        context = self.get_context_data(**kwargs)

        if self.forms['jobs'].is_valid():
            context["diff"] = self.forms['jobs'].compare()

        return self.render_to_response(context)

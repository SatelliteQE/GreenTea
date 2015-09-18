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
from django.views.generic import TemplateView
from taggit.models import Tag

from apps.core.forms import FilterForm
from apps.core.models import (RESULT_CHOICES, Author, CheckProgress, Event,
                              JobTemplate, Recipe, render_label)
from apps.taskomatic.models import TaskPeriodSchedule
from apps.waiver.forms import WaiverForm
from apps.waiver.models import Comment
from base import create_matrix

if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

logger = logging.getLogger(__name__)


class JobListObject:
    range_size = settings.RANGE_PREVIOUS_RUNS
    history_back = 0

    def __init__(self, **filters):
        self.filters = filters
        self.schedules = TaskPeriodSchedule.objects.values("period", "id", "counter")\
            .annotate(number=Count('period', distinct=True))\
            .order_by("period", "-counter")
        self.plans = {}

    def set_history(self, value=0):
        self.history_back = int(value)

    def create_matrix(self):
        for plan in self.schedules:
            key = plan["period"]
            if key not in self.plans:
                self.plans[key] = {
                    "data": [
                        plan["id"],
                    ],
                    "max_num": plan["counter"]}

                actual_max = plan["counter"] + 1
                self.plans[key]["label"] = range(
                    actual_max -
                    self.range_size -
                    self.history_back,
                    actual_max -
                    self.history_back)
            else:
                self.plans[key]["data"].append(plan["id"])

        for key, it in self.plans.items():
            it["count"] = len(it["label"])

    def execute(self):

        for key, it in self.plans.items():
            self.filters.update({
                "job__schedule__counter__in": it["label"],
                "job__schedule__id__in": it["data"],
                "job__template__is_enable": True
            })
            recipes = Recipe.objects.filter(**self.filters)\
                .select_related("job", "job__template", "arch", "distro", "job__schedule")\
                .order_by("job__template__position", "job_id")

            # remove task period from view when there are no recipes
            if len(recipes) == 0:
                del self.plans[key]
                continue

            # Initial object schedule plan
            if "object" not in it.keys():
                it["object"] = recipes[0].job.schedule.period

            objects = OrderedDict()
            for recipe in recipes:
                template_label = recipe.get_label()
                template = hashlib.sha224(
                    "%s%s" %
                    (template_label, recipe.job.template)).hexdigest()
                id_counter = recipe.job.schedule.counter
                if template not in objects:
                    label = OrderedDict([(k, None) for k in it["label"]])
                    objects[template] = {
                        "object": recipe.job.template,
                        "label": template_label,
                        "data": label,
                    }
                objects[template]["data"].update({
                    id_counter: recipe
                })
            self.plans[key]["objects"] = objects

    def get_data(self):
        self.create_matrix()
        self.execute()
        return self.plans


class JobsListView(TemplateView):
    template_name = 'jobs-list.html'

    def dispatch(self, request, *args, **kwargs):
        self.filters = {}
        self.forms = {}
        self.format = None
        return super(JobsListView, self).dispatch(request, *args, **kwargs)

    def filterEvent(self, parameters):
        form = FilterForm(parameters)
        if form.is_valid():
            if "tag" in parameters:
                self.filters['tag'] = form.cleaned_data["tag"]
            else:
                self.filters['tag'] = None
            if "search" in parameters:
                self.filters['search'] = form.cleaned_data["search"]
            else:
                self.filters['search'] = None
                self.forms['search'] = None
        self.forms['search'] = form
        self.format = parameters.get("format_output")

    def formEvent(self, parametrs):
        if "uids" in parametrs:
            self.forms['waiveFrom'] = WaiverForm(parametrs)
            if self.forms['waiveFrom'].is_valid():
                self.forms['waiveFrom'].save()
                self.forms['waiveFrom'].clean()
            else:
                logger.warning(self.forms['waiveFrom'].errors)

    def get(self, request, *args, **kwargs):
        self.filterEvent(request.GET)
        return super(self.__class__, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.formEvent(request.POST)
        self.get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        return super(self.__class__, self).render_to_response(
            context, **kwargs)

    def get_statistic(self):
        jobstag = JobTemplate.objects.filter(
            tags__slug=self.filters.get("tag"))

        cursor = connection.cursor()
        tag_query = ""
        if jobstag:
            tag_query = map(lambda x: "%d" % int(x.id), jobstag)
            tag_query = """ AND "core_job"."template_id" IN ( %s ) """ % ", ".join(
                tag_query)
        if self.filters.get('search'):
            # statistic information
            query = """SELECT date("core_job"."date") as job_date, "core_task"."result" as task_ressult, count("core_task"."result") from core_task
               LEFT JOIN "core_recipe" ON ("core_task"."recipe_id" = "core_recipe"."id")
               LEFT JOIN "core_job" ON ("core_recipe"."job_id" = "core_job"."id")
               LEFT JOIN "core_jobtemplate" ON ("core_jobtemplate"."id" = "core_job"."template_id")
               WHERE "core_job"."date" > %s AND "core_jobtemplate"."is_enable" = %s
               AND lower("core_jobtemplate"."whiteboard") LIKE lower(%s)
               GROUP BY date("core_job"."date"), "core_task"."result" ORDER BY job_date ASC, task_ressult """
            cursor.execute(query,
                           [(datetime.now().date() - timedelta(days=14)).isoformat(), True, "%%%s%%" % self.filters.get('search')])
        else:
            query = """SELECT date("core_job"."date") as job_date, "core_task"."result" as task_ressult, count("core_task"."result") from core_task
               LEFT JOIN "core_recipe" ON ("core_task"."recipe_id" = "core_recipe"."id")
               LEFT JOIN "core_job" ON ("core_recipe"."job_id" = "core_job"."id")
               LEFT JOIN "core_jobtemplate" ON ("core_jobtemplate"."id" = "core_job"."template_id")
               WHERE "core_job"."date" > %s AND "core_jobtemplate"."is_enable" = %s """ + tag_query + """
               GROUP BY date("core_job"."date"), "core_task"."result" ORDER BY job_date ASC, task_ressult """
            cursor.execute(query,
                           [(datetime.now().date() - timedelta(days=14)).isoformat(), True])

        data = cursor.fetchall()
        label = OrderedDict()
        T = lambda x: dict(RESULT_CHOICES)[x]
        for it in data:
            if not it[0] in label.keys():
                label.update({it[0]: 0})
        statistic = {
            "data": {"sum": copy(label)}, "label": copy(label)}
        for it in data:
            if not T(it[1]) in statistic['data'].keys():
                statistic['data'][T(it[1])] = copy(label)

            if it[0] in statistic['data']["sum"]:
                pass
            statistic['data'][T(it[1])][it[0]] = it[2]
            statistic['data']["sum"][it[0]] += it[2]

        data = statistic["data"]
        head = [it for it in data.keys() if it != "sum"]
        content = "date\t%s" % "\t".join(head)
        render = OrderedDict()
        for key, items in data.items():
            if key == "sum":
                continue
            for it in items:
                count = data["sum"][it]
                if it not in render:
                    render[it] = [100 * items[it] / float(count), ]
                else:
                    render[it].append(100 * items[it] / float(count))
        for key, value in render.items():
            row = "\t".join([str("%.2f" % it) for it in value])
            content += "\n%s\t%s" % (key, row)
        return content

    def render_to_response(self, context, **response_kwargs):
        # temporary return data for statis
        if self.format == "txt":
            content = self.get_statistic()
            return HttpResponse(content, content_type='text/plain')
        return super(self.__class__, self).render_to_response(
            context, **response_kwargs)

    def prepare_matrix(self, jobs, recipes, label=None):
        data, reschedule = OrderedDict(), 0
        if not label:
            label = create_matrix(settings.PREVIOUS_DAYS)
        for job in jobs:
            job.recipes = dict()
            data[job.whiteboard] = job

        for recipe in recipes:
            whiteboard = recipe.job.template.whiteboard
            lb = render_label(recipe.get_dict(), data[whiteboard].grouprecipes)
            tmp_recipe = data[whiteboard].recipes
            if lb not in tmp_recipe:
                tmp_recipe[lb] = dict()
                tmp_recipe[lb]["job"] = whiteboard
                tmp_recipe[lb]["days"] = OrderedDict()
                tmp_recipe[lb]["label"] = lb
                for d in label:
                    tmp_recipe[lb]["days"][d] = {
                        "recipe": None, "schedule": []}
            labeldate = recipe.get_date().date()
            # recipe isn't in range of date # FIXME
            if labeldate not in tmp_recipe[lb]["days"]:
                continue

            tmp_recipe[lb]["days"][labeldate]["recipe"] = recipe
            tmp_recipe[lb]["days"][labeldate]["schedule"].append(recipe.uid)
        return data

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['detailPanelHidden'] = self.request.COOKIES.get('detailHidden')
        context['detailPanelHeight'] = int(
            self.request.COOKIES.get('detailHeight', 0))
        context['detailActions'] = [Comment.ENUM_ACTION_WAIVED,
                                    Comment.ENUM_ACTION_RETURN,
                                    Comment.ENUM_ACTION_RESCHEDULE]
        context['waiveClass'] = Comment
        context['GITWEB_URL'] = settings.GITWEB_URL

        # Get all tags
        context["actualtag"] = self.filters.get("tag")
        context['tags'] = Tag.objects.all()

        # Get scheduled jobs
        filters, jobstag = {}, {}

        if self.filters.get('search'):
            filters.update({
                "job__template__whiteboard__icontains": self.filters.get('search'),
            })

        if self.filters.get("tag"):
            jobstag = JobTemplate.objects.filter(
                tags__slug=self.filters.get("tag"))
            filters.update({
                "job__template__in": jobstag,
            })

        # Get all data from database for jobs ###
        joblist = JobListObject(**filters)
        if self.request.GET.get("back"):
            joblist.set_history(self.request.GET.get("back"))
        context['plans'] = joblist.get_data()

        try:
            context['progress'] = CheckProgress.objects.order_by(
                "-datestart")[0]
        except IndexError:
            context['progress'] = None
        # Search box
        context['forms'] = self.forms.get('search', FilterForm())
        # Waive Form
        author = Author.FromUser(self.request.user)
        if author:
            waiveform = WaiverForm(initial={"username": author.name})
        else:
            waiveform = WaiverForm()
        context['waiveForm'] = self.forms.get('waiveForm', waiveform)

        # get all tags

        context["events"] = Event.objects.filter(
            is_enabled=True, datestart__lt=datetime.now,
            dateend__gt=datetime.now)
        return context

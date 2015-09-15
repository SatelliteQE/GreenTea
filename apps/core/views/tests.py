# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

"""View for tests page"""

import logging
import sys
import urllib
from datetime import date, timedelta

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import TemplateView

from apps.core.forms import FilterForm
from apps.core.models import (FAIL, Author, CheckProgress, Git, GroupOwner,
                              Task, Test, TestHistory, render_label)
from apps.core.utils.date_helpers import currentDate
from apps.taskomatic.models import TaskPeriodSchedule
from apps.waiver.forms import WaiverForm
from apps.waiver.models import Comment
from .base import create_matrix

if sys.version_info < (2, 7):
    from ordereddict import OrderedDict   #pylint: disable=import-error
else:
    from collections import OrderedDict

LOGGER = logging.getLogger(__name__)


class TestsListView(TemplateView):
    """Show all of the tests"""
    template_name = 'tests-list.html'

    def dispatch(self, request, *args, **kwargs):
        """Django uses this to initialize view object"""
        self.filters = {}
        self.forms = {}
        return super(TestsListView, self).dispatch(request, *args, **kwargs)

    def filter_event(self, parameters, *args, **kwargs):
        """Setup filtering as per options we got via GET parameters"""
        self.filters = {'onlyfail': False}
        self.forms['search'] = FilterForm(parameters)
        if 'repo' in parameters:
            self.filters['repo_id'] = parameters.get('repo')
        if 'group' in parameters:
            self.filters['group_id'] = parameters.get('group')
        if 'email' in kwargs:
            self.filters['email'] = kwargs.get('email')
        if 'search' in parameters:
            self.filters['email'] = None
            if self.forms['search'].is_valid():
                self.filters['onlyfail'] = self.forms[
                    'search'].cleaned_data["onlyfail"]
                self.filters['search'] = self.forms[
                    'search'].cleaned_data["search"]
            else:
                self.forms['search'] = None

    def form_event(self, parametrs):
        """Handle submitted waiver form"""
        if 'uids' in parametrs:
            self.forms['waiveFrom'] = WaiverForm(parametrs)
            if self.forms['waiveFrom'].is_valid():
                self.forms['waiveFrom'].save()
                self.forms['waiveFrom'] = WaiverForm()
            else:
                LOGGER.warning(self.forms['waiveFrom'].errors)

    def get(self, request, *args, **kwargs):
        """Handle GET request. I.e. displaying the page"""
        self.filter_event(request.GET, *args, **kwargs)
        return super(self.__class__, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request. I.e. submitting waiver form in our case"""
        self.form_event(request.POST)
        self.get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        """???"""
        context['forms'] = self.forms.get('search', FilterForm())
        author = Author.FromUser(self.request.user)
        if author:
            waiveform = WaiverForm(initial={"username": author.name})
        else:
            waiveform = WaiverForm()
        context['waiveForm'] = self.forms.get('waiveForm', waiveform)

        return super(self.__class__, self).render_to_response(
            context, **response_kwargs)

    def __update_context_detail_panel(self, context):
        """Load detail panel setting"""
        context['detailPanelHidden'] = self.request.COOKIES.get('detailHidden')
        context['detailPanelHeight'] = int(
            self.request.COOKIES.get('detailHeight', 0))
        context['detailActions'] = [ Comment.ENUM_ACTION_WAIVED, ]
        context['waiveClass'] = Comment
        return context

    def __get_period_ids(self):
        """Determine TaskPeriodSchedule IDs we are interested in (7 newest)"""
        periods = reversed(
            TaskPeriodSchedule.objects.all().values(
                "title", "date_create", "id", "counter")
                .order_by("-counter")[:settings.RANGE_PREVIOUS_RUNS]
        )
        return map(lambda x: x["id"], periods)

    def __get_tasks_and_tests(self, period_ids):
        """Return filtered tests and tasks (i.e. test runs) to be shown on tests.html"""
        testFilter = dict()
        taskFilter = dict()
        # taskFilter['recipe__job__template__is_enable'] = True
        # testFilter['task__recipe__job__template__is_enable'] = True
        search = self.filters.get('search', False)
        if search and len(search) > 0:
            testFilter['name__icontains'] = search
            # taskFilter['test__name__icontains'] = search
        if self.filters.get('onlyfail', False):
            testFilter['task__result__in'] = [FAIL, ]
            # TODO: This is not good solution, it should be replaced
            day = date.today() - timedelta(days=1)
            testFilter['task__recipe__job__date__gt'] = day
        if 'email' in self.filters and self.filters["email"]:
            testFilter['owner__email'] = self.filters.get('email')
            # taskFilter['test__owner__email'] = self.filters.get('email')
        if 'repo_id' in self.filters:
            taskFilter['test__git__id'] = self.filters.get('repo_id')
            testFilter["git__id"] = self.filters.get('repo_id')
        if 'group_id' in self.filters:
            taskFilter['test__groups__id'] = self.filters.get('group_id')
            testFilter["groups__id"] = self.filters.get('group_id')
        # We are interested only in tests/tasks with enabled owner (TODO: why?)
        testFilter['owner__is_enabled'] = True
        taskFilter['test__owner__is_enabled'] = True
        # Limit query to TaskPeriodSchedule-s we are interested in
        # (i.e 7 newest or something like that)
        taskFilter['recipe__job__schedule__id__in'] = period_ids

        # Load all the interesting Task-s (Task == executed Test)
        # TODO: Do we really need all these fields?
        # Note: That `annotate()` is a workaround to make results unique
        tasks = Task.objects.filter(**taskFilter).values(
            "recipe__job__template__whiteboard", "test__name", "recipe__resultrate",
            "recipe__arch__name", "test__owner__email", "recipe__uid", "recipe__job__date",
            "result", "id", "uid", "recipe", "statusbyuser",
            "recipe__job__template__grouprecipes", "recipe__arch__name",
            "recipe__whiteboard", "recipe__distro__name", "alias", "recipe__job__schedule__id")\
            .order_by("test__owner__name", "recipe__job__template__whiteboard") \
            .annotate(Count('id'))

        # Load all the Test-s
        # TODO: Why are we ordering these?
        # TODO: Cant we somehow limit this query to return only count of items
        #       per paginator settings
        tests = Test.objects.filter(**testFilter) \
            .annotate(count_fail=Count('task__result'))\
            .annotate(Count('id')).order_by("-count_fail")

        return tasks, tests

    def __get_tests_ids(self, tests):
        """Construct test IDs list on current page"""
        ids = []
        for it in tests.object_list:
            ids.append(it.id)
        return ids

    def __get_tests_per_email(self, tests, owners):
        """Construct list of tests per owner email for current page"""
        data = dict()
        for it in tests.object_list:
            if it.owner_id:
                email = owners[it.owner_id].email
            else:
                email = 'unknow@redhat.com'
            if email not in data:
                data[email] = {
                    "tests": OrderedDict(),
                    'owner': owners[it.owner_id]
                }
            data[email]["tests"][it.name] = it
            data[email]["tests"][it.name].labels = OrderedDict()
        return data

    def __expand_task_grouprecipes_template(self, task):
        """If Task-s JobTemplate have "Grouprecipes" template set (e.g. "{{arch}}"),
           render that template (i.e. get actual value for the template)"""
        tmp = {
            "arch": task["recipe__arch__name"],
            "distro": task["recipe__distro__name"],
            "distro_label": task["recipe__distro__name"],
            "whiteboard": task["recipe__whiteboard"],
            "alias": task["alias"],
        }
        return render_label(tmp, task["recipe__job__template__grouprecipes"])

    def __get_history(self, period_ids):
        history = {}
        period_oldest_list = TaskPeriodSchedule.objects.filter(id__in=period_ids)\
            .order_by("counter")
        if len(period_oldest_list):
            period_oldest = period_oldest_list[0].date_create
        else:
            period_oldest = date.today()
        changes = TestHistory.objects.filter(date__gt=period_oldest).select_related(
            "test").annotate(dcount=Count("test"))
# TODO: Fix this feaure, the dependence packages
#        deptTests = dict()
#        for test in Test.objects.filter(dependencies__in = [it.test for it in changes]):
#            for depIt in test.dependencies.all():
#                if depIt.id not in deptTests:
#                    deptTests[depIt.id] = list()
#                deptTests[depIt.id].append(depIt)
        for change in changes:
            try:
                period_id = TaskPeriodSchedule.objects.filter(
                    id__in=period_ids, date_create__gt=change.date).order_by("counter")[0].id
                if period_id not in history[change.test.id]:
                    history[change.test.id][period_id] = list()
                if change.test.id not in history:
                    history[change.test.id] = dict()
            except IndexError:
                return history
            history[change.test.id][period_id].insert(0, change)

# depList = list() # Test.objects.filter(dependencies=change.test).values("id")
#            for depchange in depList:
#                if not history.has_key(depchange['id']):
#                    history[depchange['id']] = {}
#                if not history[depchange['id']].has_key(day):
#                    history[depchange['id']][day] = []
#                history[depchange['id']][day].append(change)
        return history

    def get_context_data(self, **kwargs):
        """Do all the work"""
        context = super(self.__class__, self).get_context_data(**kwargs)
        # Load detail panel setting
        context = self.__update_context_detail_panel(context)
        # Load URL to tests git storage
        context['GITWEB_URL'] = settings.GITWEB_URL
        # Owners
        owners = dict([(it.id, it)
                       for it in Author.objects.filter(is_enabled=True) \
                         .annotate(dcount=Count('test'))])

        # Determine TaskPeriodSchedule IDs we are interested in (~7 newest)
        period_ids = self.__get_period_ids()

        # Load history we display for each test
        history = self.__get_history(period_ids)

        # Determine filtered tests and tasks
        tasks, tests = self.__get_tasks_and_tests(period_ids)

        # Determine Test IDs we are interested in as per paginator
        paginator = Paginator(tests, settings.PAGINATOR_OBJECTS_ONPAGE)
        testlist = paginator.page(int(self.request.GET.get('page', 1)))

        # Construct list of tests per owner email for current page
        data = self.__get_tests_per_email(testlist, owners)

        # Limit Task-s we are working with only to Test-s shown on current page
        tasks = tasks.filter(test__in=self.__get_tests_ids(testlist))

        # Process all the Task-s
        for it in tasks:
            # Using reference just make a shortcut to "data..." structure
            test = data[it["test__owner__email"]]["tests"][it["test__name"]]

            # Get label we will use for this task
            test_label = (
                it["recipe__job__template__whiteboard"],
                self.__expand_task_grouprecipes_template(it)
            )

            # Create empty matrix
            if test_label not in test.labels:
                test.labels[test_label] = OrderedDict()
                for period_id in period_ids:
                    test.labels[test_label][period_id] = None

            # Period we are working on now
            period_id = it["recipe__job__schedule__id"]

            # Skip Task-s which were run in different periods than what we are displaying
            if period_id not in test.labels[test_label]:
                continue

            # Check if we were rescheduled
            reschedule = 0
            if test.labels[test_label][period_id]:
                reschedule = test.labels[test_label][period_id].reschedule + 1

            # Fill matrix with actual data (i.e. info about Task)
            test.labels[test_label][period_id] = Task(
                id=it["id"],
                uid=it["uid"],
                result=it["result"],
                statusbyuser=it["statusbyuser"],
            )
            test.labels[test_label][period_id].resultrate = it["recipe__resultrate"]
            test.labels[test_label][period_id].recipe_uid = "%s" % it["recipe__uid"]
            test.labels[test_label][period_id].reschedule = reschedule

        try:
            progress = CheckProgress.objects.order_by("-datestart")[0]
        except IndexError:
            progress = None

        urllist = filter(
            lambda x_y: x_y[0] != "page", self.request.GET.copy().items())

        if self.filters.get('onlyfail', False):
            context["tests_bad"] = tests[:10]

        context.update({
            "data": data,
            "owners": owners,
            "label": period_ids,
            "tests": testlist,
            "paginator": paginator,
            "progress": progress,
            "history": history,
            "urlstring": urllib.urlencode(dict(urllist)),
            "repos": Git.objects.all().order_by('name'),
            "groups": GroupOwner.objects.all().order_by('name'),
        })
        return context

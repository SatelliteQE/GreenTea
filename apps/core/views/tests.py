# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013


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
from base import create_matrix

if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

logger = logging.getLogger(__name__)


class TestsListView(TemplateView):
    template_name = 'tests-list.html'

    # !!! INITIAL DATA in dispatch, this method call before get, post, delte, atd !!!
    def dispatch(self, request, *args, **kwargs):
        self.filters = {}
        self.forms = {}
        return super(TestsListView, self).dispatch(request, *args, **kwargs)

    def filterEvent(self, parameters, *args, **kwargs):
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

    def formEvent(self, parametrs):
        if 'uids' in parametrs:
            self.forms['waiveFrom'] = WaiverForm(parametrs)
            if self.forms['waiveFrom'].is_valid():
                self.forms['waiveFrom'].save()
                self.forms['waiveFrom'] = WaiverForm()
            else:
                logger.warning(self.forms['waiveFrom'].errors)

    def get(self, request, *args, **kwargs):
        self.filterEvent(request.GET, *args, **kwargs)
        return super(self.__class__, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.formEvent(request.POST)
        self.get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        # Search box
        context['forms'] = self.forms.get('search', FilterForm())
        author = Author.FromUser(self.request.user)
        if author:
            waiveform = WaiverForm(initial={"username": author.name})
        else:
            waiveform = WaiverForm()
        context['waiveForm'] = self.forms.get('waiveForm', waiveform)

        return super(self.__class__, self).render_to_response(
            context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['detailPanelHidden'] = self.request.COOKIES.get('detailHidden')
        context['detailPanelHeight'] = int(
            self.request.COOKIES.get('detailHeight', 0))
        context['detailActions'] = [Comment.ENUM_ACTION_WAIVED, ]
        context['waiveClass'] = Comment
        context['GITWEB_URL'] = settings.GITWEB_URL
        # Tests
        testFilter = dict()
        # testFilter['task__recipe__job__template__is_enable'] = True
        # Tasks
        taskFilter = dict()
        # taskFilter['recipe__job__template__is_enable'] = True
        # Owners
        owners = dict([(it.id, it)
                       for it in Author.objects.filter(is_enabled=True).annotate(dcount=Count('test'))])
        # date Labels
        dates_label = create_matrix(settings.PREVIOUS_DAYS + 1)
        # History
        history = dict()
        minDate = currentDate() - timedelta(days=settings.PREVIOUS_DAYS + 7)
        changes = TestHistory.objects.filter(date__gt=minDate).select_related(
            'test').annotate(dcount=Count('test'))
# TODO: Fix this feaure, the dependence packages
#        deptTests = dict()
#        for test in Test.objects.filter(dependencies__in = [it.test for it in changes]):
#            for depIt in test.dependencies.all():
#                if depIt.id not in deptTests:
#                    deptTests[depIt.id] = list()
#                deptTests[depIt.id].append(depIt)
        for change in changes:
            day = change.date.date()
            if change.date.hour > 20:
                day = day + timedelta(days=1)
            for lday in dates_label:
                if lday >= day:
                    day = lday
                    break
            if change.test.id not in history:
                history[change.test.id] = dict()
            if day not in history[change.test.id]:
                history[change.test.id][day] = list()
            history[change.test.id][day].insert(0, change)
# depList = list() # Test.objects.filter(dependencies=change.test).values("id")
#            for depchange in depList:
#                if not history.has_key(depchange['id']):
#                    history[depchange['id']] = {}
#                if not history[depchange['id']].has_key(day):
#                    history[depchange['id']][day] = []
#                history[depchange['id']][day].append(change)
        # apply filter
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

        # Determine TaskPeriodSchedule IDs we are interested in (7 newest)
        start, end = 0, 7
        periods = TaskPeriodSchedule.objects.all().values(
            "title", "date_create", "id", "counter").order_by("title", "-date_create")
        period_ids = map(lambda x: x["id"], periods)
        taskFilter['recipe__job__schedule__id__in'] = period_ids

        # We are interested only in tasks with owner set (FIXME: why?)
        taskFilter['test__owner__is_enabled'] = True

        # Load all the interesting Task-s (task is executed Test)
        # TODO: Do we really need all these fields?
        # TODO: Whats the `annotate()` for?
        tasks = Task.objects.filter(**taskFilter).values(
            "recipe__job__template__whiteboard", "test__name", "recipe__resultrate", "recipe__arch__name",
            "test__owner__email", "recipe__uid", "recipe__job__date", "result", "id", "uid", "recipe",
            "statusbyuser", "recipe__job__template__grouprecipes", "recipe__arch__name",
            "recipe__whiteboard", "recipe__distro__name", "alias", "recipe__job__schedule__id")\
            .order_by("test__owner__name", "recipe__job__template__whiteboard") \
            .annotate(Count('id'))

        # We are interested only in tasks with owner set (FIXME: why?)
        testFilter['owner__is_enabled'] = True

        # Load all the Test-s
        # TODO: Why are we ordering these?
        # TODO: Cant we somehow lomit this query to return only count of items
        # per paginator settings
        tests = Test.objects.filter(**testFilter) \
            .annotate(count_fail=Count('task__result'))\
            .annotate(Count('id')).order_by("-count_fail")

        # Determine Test IDs we are interested in as per paginator
        paginator = Paginator(tests, settings.PAGINATOR_OBJECTS_ONPAGE)
        testlist = paginator.page(int(self.request.GET.get('page', 1)))
        ids = []
        data = dict()
        for it in testlist.object_list:
            email = owners[
                it.owner_id].email if it.owner_id else "unknow@redhat.com"
            if email not in data:
                data[email] = dict(
                    {"tests": OrderedDict(), 'owner': owners[it.owner_id]})
            ids.append(it.id)
            it.labels = OrderedDict()
            data[email]["tests"][it.name] = it

        # Limit Task-s we are working with only to Test-s shown on current page
        tasks = tasks.filter(test__in=ids)

        # Some variable... TODO
        stat = {"tasks": len(tasks), "tests": paginator.count}

        # Process all the Task-s
        for it in tasks:
            email = it["test__owner__email"]

            # Skip Task-s owned by somebody else than we want and with
            # unrelated name
            if email not in data or \
               it["test__name"] not in data[email]["tests"]:
                continue

            # Using refference just make a shortcut to "data..." structure
            test = data[email]["tests"][it["test__name"]]

            # If Task-s JobTemplate have "Grouprecipes" template set
            # (e.g. "{{arch}}"), render that template (i.e. get actual
            # value for the template)
            lb = render_label({
                "arch": it["recipe__arch__name"],
                "distro": it["recipe__distro__name"],
                "distro_label": it["recipe__distro__name"],
                "whiteboard": it["recipe__whiteboard"],
                "alias": it["alias"],
            }, it["recipe__job__template__grouprecipes"])
            test_label = (it["recipe__job__template__whiteboard"], lb)

            # Create empty matrix
            # TODO: When can this "if ..." expression fail? Why is it here?
            if test_label not in test.labels:
                test.labels[test_label] = OrderedDict()
                for period_id in period_ids:
                    test.labels[test_label][period_id] = None

            # Using refference just make a shortcut to "test..." structure
            label = test.labels[test_label]

            period_id = it["recipe__job__schedule__id"]
            if period_id not in label:
                continue

            # Handle reschedules in a way... TODO
            reschedule = 0
            if label[period_id]:
                reschedule = label[period_id].reschedule + 1

            # Fill matrix with actual data (i.e. info about Task)
            label[period_id] = Task(
                id=it["id"],
                uid=it["uid"],
                result=it["result"],
                statusbyuser=it["statusbyuser"],
            )
            label[period_id].resultrate = it["recipe__resultrate"]
            label[period_id].recipe_uid = "%s" % it["recipe__uid"]
            label[period_id].reschedule = reschedule

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
            "stat": stat,
            "history": history,
            "urlstring": urllib.urlencode(dict(urllist)),
            "repos": Git.objects.all().order_by('name'),
            "groups": GroupOwner.objects.all().order_by('name'),
        })
        return context

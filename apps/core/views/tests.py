# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

"""View for tests page"""

import logging
from datetime import date

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Max
from django.views.generic import TemplateView

from apps.core.forms import FilterForm
from apps.core.models import (Author, CheckProgress, Git, GroupOwner, Task,
                              Test, TestHistory, render_label)
from apps.taskomatic.models import TaskPeriod, TaskPeriodSchedule
from apps.waiver.forms import WaiverForm
from apps.waiver.models import Comment

logger = logging.getLogger(__name__)


def get_matching_period_for_change(periods, change):
    """Takes a list of period objects and a change object and based on
       period.date_create and change.date returns period directly
       following the change. If the change happened before first period
       (this is an exception) of after last period ("including" for both),
       exception is raised. So when you are generating list of periods as
       an input for this function, make sure to include one period before
       oldest one."""
    periods = periods.order_by('counter')
    if change.date <= periods.earliest('counter').date_create \
            or change.date >= periods.latest('counter').date_create:
        raise Exception("Change %s do not fit among %s periods" %
                        (change, periods))
    for i in range(len(periods) - 1):
        if periods[i].date_create < change.date < periods[i + 1].date_create:
            return periods[i + 1]


def get_history(period_ids):
    history = {}
    # We are interested in one period before as well, because we want to
    # catch changes which happened right before our first period
    period_ids_one_prev_added = period_ids
    if period_ids:
        period_ids_one_prev_added += [min(period_ids) - 1]
    # Get time/date limits we will use when getting list of changes
    periods_age_list = TaskPeriodSchedule.objects.filter(
        id__in=period_ids_one_prev_added)
    if len(periods_age_list):
        period_oldest_date = periods_age_list.earliest('counter').date_create
        period_newest_date = periods_age_list.latest('counter').date_create
    else:
        period_oldest_date = date.today()
        period_newest_date = date.today()
    # FIXME: We should be checking for tags and not commits. Tags are
    #        closer to the test build&submission date than commits
    #        (you can commit and not build the test)
    changes = TestHistory.objects.filter(date__gt=period_oldest_date, date__lt=period_newest_date)\
        .annotate(dcount=Count("test"))
# TODO: Fix this feaure, the dependence packages
#    deptTests = dict()
#    for test in Test.objects.filter(dependencies__in = [it.test for it in changes]):
#        for depIt in test.dependencies.all():
#            if depIt.id not in deptTests:
#                deptTests[depIt.id] = list()
#            deptTests[depIt.id].append(depIt)
    for change in changes:
        if change.test_id not in history:
            history[change.test_id] = dict()
        period_id = get_matching_period_for_change(
            periods_age_list, change).counter
        if period_id not in history[change.test_id]:
            history[change.test_id][period_id] = list()
        history[change.test_id][period_id].insert(0, change)
# depList = list() # Test.objects.filter(dependencies=change.test).values("id")
#        for depchange in depList:
#            if not history.has_key(depchange['id']):
#                history[depchange['id']] = {}
#            if not history[depchange['id']].has_key(day):
#                history[depchange['id']][day] = []
#            history[depchange['id']][day].append(change)
    return history


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
                logger.warning(self.forms['waiveFrom'].errors)

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
        context['detailActions'] = [Comment.ENUM_ACTION_WAIVED, ]
        context['waiveClass'] = Comment
        return context

    def __get_period_ids(self, periodschedules):
        """Determine period schedule IDs we are interested in based on
           object provided by __get_period_tree()"""
        periodschedule_ids = []
        for periodschedule in periodschedules.values():
            periodschedule_ids += [i['id'] for i in periodschedule]
        logger.debug("TestsListView.__get_period_ids returns: %s" %
                     periodschedule_ids)
        return periodschedule_ids

    def __get_period_tree(self):
        """Return dict of periods we are interested in:
            {<period_id>:
                [
                    {'id': ..., 'counter': ..., 'period__title': ...},
                    ...
                ],
             ...}"""
        periodschedules = {}
        for period in TaskPeriod.objects.only("id").all():
            periodschedules[period.id] = []
            for p in TaskPeriodSchedule.objects\
                    .filter(period_id=period.id)\
                    .values("id", "counter", "period__title")\
                    .order_by("-counter")[:settings.RANGE_PREVIOUS_RUNS]:
                periodschedules[period.id].append({
                    'id': p['id'],
                    'counter': p['counter'],
                    'period__title': p['period__title'],
                })
        logger.debug("TestsListView.__get_period_tree returns: %s" %
                     periodschedules)
        return periodschedules

    def __get_test_ids(self):
        """Return filtered tests to be shown on tests.html"""
        testFilter = {}
        # testFilter['task__recipe__job__template__is_enable'] = True
        search = self.filters.get('search', False)
        if search and len(search) > 0:
            testFilter['name__icontains'] = search
        if 'email' in self.filters and self.filters["email"]:
            testFilter['owner__email'] = self.filters.get('email')
        if 'repo_id' in self.filters:
            testFilter["git__id"] = self.filters.get('repo_id')
        if 'group_id' in self.filters:
            testFilter["groups__id"] = self.filters.get('group_id')
        # Load all the Test-s
        # TODO: Why are we ordering these?
        # TODO: Cant we somehow limit this query to return only count of items
        #       per paginator settings
        tests = Test.objects.filter(**testFilter).only("id").values("id")
        # this just makes the list uniqe
        tests = sorted(set(it['id'] for it in tests))
        logger.debug("TestsListView.__get_test_ids returns: %s" % tests)
        return tests

    def get_context_data(self, **kwargs):
        # TODO: some table styling + changes in the tests
        context = super(self.__class__, self).get_context_data(**kwargs)
        # Update context for details panel
        context = self.__update_context_detail_panel(context)
        # Determine task period schedules we are going to use
        periodschedules = self.__get_period_tree()
        # Determine all available test IDs filtered by our filters
        test_ids_all = self.__get_test_ids()
        # Trim test IDs as per paginator
        paginator = Paginator(test_ids_all, settings.PAGINATOR_OBJECTS_ONPAGE)
        test_ids = paginator.page(int(self.request.GET.get('page', 1)))
        # Load and reorder data about tests
        data = self.prepare_matrix(
            test_ids=test_ids, periodschedules=periodschedules)
        # Return page
        context.update({
            'data': data,
            'periodschedules': periodschedules,
            'test_ids': test_ids,
            'paginator': paginator,
            'progress': CheckProgress.objects.all().aggregate(Max('datestart'))['datestart__max'],
            'owners': Author.objects.filter(is_enabled=True).annotate(dcount=Count('test')).order_by("-dcount"),
            'repos': Git.objects.all().order_by('name'),
            'groups': GroupOwner.objects.all().order_by('name'),
        })
        return context

    def prepare_matrix(self, test_ids=[], periodschedules=[]):
        """Load info about  from DB and return it in template friendly object."""
        out_dict = {}   # template friendly data structure
        # Determine plain list of period schedule IDs
        periodschedule_ids = self.__get_period_ids(periodschedules)
        # Set list of tables and fields for the query and create initial
        # version of the filter (filter by "test_id" will be added later
        # in the loop below)
        relations = ['test', 'test__owner', 'test__git', 'recipe',
                     'recipe__arch', 'recipe__distro', 'recipe__job',
                     'recipe__job__template', 'recipe__job__schedule']
        fields = [
            'test__id', 'test__name', 'test__folder',
            'test__owner__id', 'test__owner__name', 'test__owner__email',
            'test__git__id', 'test__git__localurl',
            'test__groups__name',
            'id', 'uid', 'result', 'status', 'statusbyuser', 'alias',
            'recipe__id', 'recipe__uid', 'recipe__status', 'recipe__resultrate', 'recipe__whiteboard', 'recipe__statusbyuser',
            'recipe__arch__name',
            'recipe__distro__name',
            'recipe__job__id', 'recipe__job__uid',
            'recipe__job__template__id', 'recipe__job__template__whiteboard', 'recipe__job__template__grouprecipes',
            'recipe__job__schedule__id', 'recipe__job__schedule__counter', 'recipe__job__schedule__period_id',
        ]
        filters = {}
        filters['recipe__job__schedule__id__in'] = periodschedule_ids
        # Now process all the tests
        for test_id in test_ids:
            filters['test_id'] = test_id
            data = Task.objects.filter(
                **filters).select_related(*relations).only(*fields)
            # Reorder data into tempate friendly data structure
            for i in data:
                # Popupate tests
                if i.test.id not in out_dict:
                    out_dict[i.test.id] = {
                        'name': i.test.name,
                        'owner__name': i.test.owner.name,
                        'owner__email': i.test.owner.email,
                        'get_absolute_url': i.test.get_absolute_url(),
                        'get_reposituory_url': i.test.get_reposituory_url(),
                        'get_detail_url': i.test.get_detail_url(),
                        'test__groups__name': [],
                        'data': {},
                    }
                # Populate test's groups
                if i.test.groups.name not in out_dict[i.test.id]['test__groups__name']:
                    out_dict[i.test.id]['test__groups__name'].append(
                        i.test.groups.name)
                # Populate period schedules (because one test can run in 'Daily
                # automation' and 'Weekly automation' and...)
                if i.recipe.job.schedule.period_id not in out_dict[i.test.id]['data']:
                    title = ''
                    for p in periodschedules[i.recipe.job.schedule.period_id]:
                        if p['id'] == i.recipe.job.schedule.id:
                            title = p['period__title']
                            break
                    out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id] = {
                        'title': title,
                        'data': {},
                    }
                # Popupate job (just general info common for more nightly runs)
                if i.recipe.job.template.id not in out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data']:
                    out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data'][i.recipe.job.template.id] = {
                        'template__whiteboard': i.recipe.job.template.whiteboard,
                        'data': {},
                    }
                # Popupate recipe (just general info common for more nightly
                # runs)
                tmp = {
                    "arch": i.recipe.arch.name,
                    "distro": i.recipe.distro.name,
                    "distro_label": i.recipe.distro.name,
                    "whiteboard": i.recipe.whiteboard,
                    "alias": i.alias,
                }
                recipe_matcher = render_label(
                    tmp, i.recipe.job.template.grouprecipes)
                if recipe_matcher not in out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data'][i.recipe.job.template.id]['data']:
                    out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data'][i.recipe.job.template.id]['data'][recipe_matcher] = {
                        'data': {},
                    }
                # Populate schedule
                if i.recipe.job.schedule.id not in out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data'][i.recipe.job.template.id]['data'][recipe_matcher]['data']:
                    out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data'][i.recipe.job.template.id]['data'][recipe_matcher]['data'][i.recipe.job.schedule.id] = {
                        'counter': i.recipe.job.schedule.counter,
                        'data': {},
                    }
                # Populate task (i.e. test run)
                if i.id not in out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data'][i.recipe.job.template.id]['data'][recipe_matcher]['data'][i.recipe.job.schedule.id]['data']:
                    out_dict[i.test.id]['data'][i.recipe.job.schedule.period_id]['data'][i.recipe.job.template.id]['data'][recipe_matcher]['data'][i.recipe.job.schedule.id]['data'][i.id] = {
                        'uid': i.uid,
                        'result': i.get_result(),
                        'status': i.recipe.get_status(),
                        'is_running': i.recipe.is_running(),
                        'recipe__id': i.recipe.id,
                        'recipe__uid': i.recipe.uid,
                        'recipe__result': i.recipe.get_result(),
                        'recipe__resultrate': i.recipe.resultrate,
                        'recipe__job__uid': i.recipe.job.uid,
                    }
        return out_dict

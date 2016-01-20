import logging
from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView
from apps.taskomatic.models import TaskPeriodSchedule, TaskPeriod
from apps.core.models import (JobTemplate, RecipeTemplate, Recipe, Task, render_label)

logger = logging.getLogger(__name__)

class RecipeHistoryView(TemplateView):
    """Shows history of individual tasks from a recipe given in URL"""
    template_name = 'recipe-history.html'


    def dispatch(self, request, *args, **kwargs):
        """Django uses this to initialize view object"""
        self.filters = {}
        self.forms = {}
        return super(RecipeHistoryView, self).dispatch(request, *args, **kwargs)


    def __get_period_ids(self, periodschedules):
        """Determine period schedule IDs we are interested in based on
           object provided by __get_period_tree()"""
        periodschedule_ids = []
        for periodschedule in periodschedules.values():
            periodschedule_ids += [i['id'] for i in periodschedule]
        logger.debug("TestsListView.__get_period_ids returns: %s" % periodschedule_ids)
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
                    .values("id", "counter", "period__title", "date_create")\
                    .order_by("-counter")[:settings.RANGE_PREVIOUS_RUNS]:
                periodschedules[period.id].append({
                    'id': p['id'],
                    'counter': p['counter'],
                    'period__title': p['period__title'],
                    'date_create': p['date_create'],
                })
        logger.debug("TestsListView.__get_period_tree returns: %s" % periodschedules)
        import pprint
        pprint.pprint(periodschedules)
        return periodschedules


    def __get_job_template(self, jid):
        """Verify job template with ID provided in URL exists"""
        job_template_id = int(jid)
        try:
            job_template = JobTemplate.objects.get(id=job_template_id)
        except RecipeTemplate.DoesNotExist:
            raise Http404
        return job_template

    def get_context_data(self, **kwargs):
        """Load required data"""

        # Ensure JobID we got in URL is valid
        job_template = self.__get_job_template(kwargs['id'])

        # Initialize context data
        context = super(self.__class__, self).get_context_data(**kwargs)

        # Get latest runs
        periodschedules = self.__get_period_tree()
        periodschedule_ids = self.__get_period_ids(periodschedules)

        # Get all latest tasks from job
        filters = {}
        filters['recipe__job__template__id'] = job_template.id
        filters['recipe__job__schedule__counter__in'] = periodschedule_ids
        related = ['test', 'recipe', 'recipe__arch', 'recipe__distro', 'recipe__job__template', 'recipe__job__schedule']
        only = [
            'id', 'uid', 'statusbyuser', 'result', 'alias',
            'test__name',
            'recipe__uid', 'recipe__whiteboard',
            'recipe__arch__name',
            'recipe__distro__name',
            'recipe__job__template__grouprecipes',
            'recipe__job__schedule__id', 'recipe__job__schedule__period_id',
        ]
        tasks = Task.objects.filter(**filters).select_related(*related).only(*only)

        # Reorder all tasks into template friendly structure
        out_dict = dict()
        for task in tasks:
            # Populate period schedules (because one test can run in 'Daily automation' and 'Weekly automation' and...)
            if task.recipe.job.schedule.period_id not in out_dict:
                title = ''
                for p in periodschedules[task.recipe.job.schedule.period_id]:
                    if p['id'] == task.recipe.job.schedule.id:
                        title = p['period__title']
                        break
                out_dict[task.recipe.job.schedule.period_id] = {
                    'title': title,
                    'data': {},
                }
            shortcut = out_dict[task.recipe.job.schedule.period_id]['data']

            # Construct recipe name
            tmp = {
                "arch": task.recipe.arch.name,
                "distro": task.recipe.distro.name,
                "distro_label": task.recipe.distro.name,
                "whiteboard": task.recipe.whiteboard,
                "alias": task.alias,
            }
            recipe_name = render_label(tmp, task.recipe.job.template.grouprecipes)

            # Create new recipe if needed
            if recipe_name not in shortcut:
                shortcut[recipe_name] = dict()
            # Create new task if needed
            if task.test.name not in shortcut[recipe_name]:
                shortcut[recipe_name][task.test.name] = dict()

            # Assign task to the right field in table
            shortcut[recipe_name][task.test.name][task.recipe.job.schedule.id] = task

        # Return page
        context.update({
            'job_template': job_template,
            'periodschedules': periodschedules,
            'recipes': out_dict,
        })
        return context

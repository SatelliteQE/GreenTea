import logging

from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView

from apps.core.models import JobTemplate, RecipeTemplate, Task
from apps.taskomatic.models import TaskPeriod, TaskPeriodSchedule

logger = logging.getLogger(__name__)


class JobHistoryView(TemplateView):
    """Shows history of individual tasks from a job given in URL"""
    template_name = 'job-history.html'

    def dispatch(self, request, *args, **kwargs):
        """Django uses this to initialize view object"""
        self.filters = {}
        self.forms = {}
        return super(JobHistoryView, self).dispatch(request, *args, **kwargs)

    def __get_period_ids(self, periodschedules):
        """Determine period schedule IDs we are interested in based on
           data provided by __get_period_tree()"""
        periodschedule_ids = []
        for periodschedule in periodschedules.values():
            periodschedule_ids += [i.id for i in periodschedule]
        return periodschedule_ids

    def __get_period_tree(self):
        """Return dict of relevant period schedules by period. All is Django ORM objects:
           {<period>: <period_schedule list>, ...}"""
        periodschedules = {}
        for period in TaskPeriod.objects.only("id", "title").all():
            periodschedules[period] = TaskPeriodSchedule.objects\
                .filter(period_id=period.id)\
                .only("id", "counter", "date_create")\
                .order_by("-counter")[:settings.RANGE_PREVIOUS_RUNS]
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
        filters['recipe__job__schedule__id__in'] = periodschedule_ids
        related = ['test', 'test__git', 'recipe', 'recipe__arch', 'recipe__distro',
                   'recipe__job__template', 'recipe__job__schedule', 'recipe__job__schedule__period']
        only = [
            'id', 'uid', 'statusbyuser', 'result', 'alias',
            'test__name', 'test__folder', 'test__git_id',
            'test__git__name', 'test__git__url', 'test__git__localurl',
            'recipe__uid', 'recipe__whiteboard',
            'recipe__arch__name',
            'recipe__distro__name',
            'recipe__job__template__grouprecipes',
            'recipe__job__schedule__id', 'recipe__job__schedule__period_id',
            'recipe__job__schedule__period__id',
        ]
        out = Task.objects.filter(
            **filters).select_related(*related).only(*only)

        # Reorder data we got into template friendly structure
        out_dict = dict()
        for task in out:
            # Populate period schedules (because one test can run in 'Daily
            # automation' and 'Weekly automation' and...)
            if task.recipe.job.schedule.period not in out_dict:
                out_dict[task.recipe.job.schedule.period] = dict()

            # Create new recipe if needed
            task_recipe = task.recipe.get_label()
            if task_recipe not in out_dict[task.recipe.job.schedule.period]:
                out_dict[task.recipe.job.schedule.period][task_recipe] = dict()

            # Create new task if needed
            if task.test not in out_dict[
                    task.recipe.job.schedule.period][task_recipe]:
                out_dict[task.recipe.job.schedule.period][
                    task_recipe][task.test] = dict()

            # Assign task to the right field in table
            out_dict[task.recipe.job.schedule.period][task_recipe][
                task.test][task.recipe.job.schedule.id] = task

        # Return page
        context.update({
            'job_template': job_template,
            'periodschedules': periodschedules,
            'data': out_dict,
        })
        return context

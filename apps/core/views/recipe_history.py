from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView
from apps.taskomatic.models import TaskPeriodSchedule
from apps.core.models import (JobTemplate, RecipeTemplate, Recipe, Task)


class RecipeHistoryView(TemplateView):
    """Shows history of individual tasks from a recipe given in URL"""
    template_name = 'recipe-history.html'

    def dispatch(self, request, *args, **kwargs):
        """Django uses this to initialize view object"""
        self.filters = {}
        self.forms = {}
        return super(RecipeHistoryView, self).dispatch(request, *args, **kwargs)

    def __get_period_ids(self):
        """Determine TaskPeriodSchedule IDs we are interested in (7 newest)"""
        periods = reversed(
            TaskPeriodSchedule.objects.all().values(
                "title", "date_create", "id", "counter")
                .order_by("-counter")[:settings.RANGE_PREVIOUS_RUNS]
        )
        return map(lambda x: x["id"], periods)

    def get_context_data(self, **kwargs):
        """Load required data"""

        # find job template
        job_template_id = int(kwargs['id'])
        try:
            job_template = JobTemplate.objects.get(id=job_template_id)
        except RecipeTemplate.DoesNotExist:
            raise Http404
        # Initialize context data
        context = super(self.__class__, self).get_context_data(**kwargs)

        # get latest run ids:
        last_run = job_template.schedule.taskperiodschedule_set.last().counter
        period_ids = range(last_run+1-settings.RANGE_PREVIOUS_RUNS, last_run+1)

        # get all latest tasks from job
        tasks = Task.objects.filter(recipe__job__template__id=job_template_id,
                                    recipe__job__schedule__counter__in=period_ids)\
            .prefetch_related('recipe__job__schedule', 'test')

        data = dict()
        # process all tasks
        for task in tasks:

            # position of task in the table
            period = task.recipe.job.schedule.counter #scheudle_id
            # period = task.recipe.job.schedule_id TODO yohle je blbe
            recipe_name = task.recipe.whiteboard
            task_name = task.test.name

            # add new recipe if needed
            if recipe_name not in data:
                data[recipe_name] = dict()
            # add new task if needed
            if task_name not in data[recipe_name]:
                data[recipe_name][task_name] = dict()
                # alocate table filed for all
                for p in period_ids:
                    data[recipe_name][task_name][p] = None

            # assign task to the right field in table
            data[recipe_name][task_name][period] = task

        # workaround
        recipe_template = None

        context.update({'recipetemplate': recipe_template, 'period_ids': period_ids, 'recipes': data})
        return context

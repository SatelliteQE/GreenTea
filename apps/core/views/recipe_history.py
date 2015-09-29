from django.conf import settings
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
        recipe_template_id = int(kwargs['id'])
        recipe_template = RecipeTemplate.objects.get(id=recipe_template_id)
        ###print ">>> recipe_template:", recipe_template, dir(recipe_template)
        job_template = JobTemplate.objects.get(id=recipe_template.jobtemplate_id)
        job_template_id = job_template.id
        ###print ">>> job_template:", job_template#, dir(job_template)
        # Task period IDs we are interested in
        period_ids = self.__get_period_ids()
        ###print ">>> period_ids:", period_ids
        # Load Tasks for given recipe and periods
        tasks = Task.objects.filter(recipe__job__template__id=job_template_id, recipe__whiteboard=recipe_template.name, recipe__job__schedule__id__in=period_ids)   # FIXME: matching recipe to recipe_template by whiteboard? C'mon man!
        print ">>> tasks:", tasks
        tests_distinct = tasks.values("test__name").order_by("uid").distinct()   # FIXME: what to do when there is one task twice in the recipe?
                                                                                 # FIXME: Ordering of the resulting table is not correct as well
        ###print ">>> tasks_distinct:", tasks_distinct
        # data = {
        #   <test1>: {
        #     <period1>: <task1.1>,
        #     <period2>: <task1.2>,
        #     ...
        #   },
        #   <test2>: {
        #     ...
        #   }
        # }
        data = {}
        for test in tests_distinct:
          test_id = test['test__name']
          if test_id not in data:
            data[test_id] = {}
            for period in period_ids:
              data[test_id][period] = []
          for task in tasks:
            period = task.recipe.job.schedule_id
            data[test_id][period] = task
        ###print ">>> data:", data

        #tasks = Task.objects.filter(**taskFilter).values(
        #    "recipe__job__template__whiteboard", "test__name", "recipe__resultrate",
        #    "recipe__arch__name", "test__owner__email", "recipe__uid", "recipe__job__date",
        #    "result", "id", "uid", "recipe", "statusbyuser",
        #    "recipe__job__template__grouprecipes", "recipe__arch__name",
        #    "recipe__whiteboard", "recipe__distro__name", "alias", "recipe__job__schedule__id")\
        #    .order_by("test__owner__name", "recipe__job__template__whiteboard") \
        #    .annotate(Count('id'))
        # FIXME
        # Initialize and fill context variable
        context = super(self.__class__, self).get_context_data(**kwargs)
        context.update({'recipetemplate': recipe_template, 'period_ids': period_ids, 'tasks': data})
        return context

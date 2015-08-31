# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import logging

from django.views.generic import TemplateView

from apps.core.forms import JobForm

logger = logging.getLogger(__name__)


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

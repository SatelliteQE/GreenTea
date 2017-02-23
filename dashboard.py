"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'tttt.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from grappelli.dashboard import Dashboard, modules
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):

    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        self.children.append(modules.Group(
            _('Group: Applications'),
            column=1,
            collapsible=True,
            children=[
                modules.AppList(
                    _('Templates'),
                    column=1,
                    collapsible=False,
                    models=(
                        'apps.core.models.Event',
                        'apps.core.models.Test',
                        'apps.report.models.Report',
                        'apps.core.models.GroupTemplate',
                        'apps.core.models.DistroTemplate',
                        'apps.core.models.JobTemplate',
                        'apps.core.models.RecipeTemplate',
                        'apps.core.models.TaskTemplate',
                        'apps.core.models.TaskRoleEnum',
                        'taggit.models.Tag',
                    ),
                ),
                modules.AppList(
                    _('Backend'),
                    column=1,
                    collapsible=False,
                    models=(
                        'apps.taskomatic.models.TaskPeriod',
                    ),
                ),
                modules.AppList(
                    _('Hisotry'),
                    column=1,
                    collapsible=False,
                    models=(
                        'apps.waiver.models.Comment',
                        'apps.core.models.TestHistory',
                        'apps.core.models.CheckProgress',
                        'apps.taskomatic.models.Task',
                        'apps.taskomatic.models.TaskPeriodSchedule',
                    ),
                ),
                modules.AppList(
                    _('Results'),
                    column=1,
                    collapsible=False,
                    models=(
                        'apps.core.models.Job',
                        'apps.core.models.Recipe',
                        'apps.core.models.Task',
                        'apps.core.models.Distro',
                        'apps.core.models.Arch',
                        'apps.core.models.Git',
                        'apps.core.models.Author',
                        'apps.core.models.GroupOwner',
                        'apps.core.models.System',
                        'apps.core.models.TestHistory',
                    ),
                ),
                modules.AppList(
                    _('Performence'),
                    column=1,
                    collapsible=False,
                    models=(
                        'apps.api.models.Performance',
                    ))
            ]
        ))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Administration'),
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            column=2,
            children=[
                {
                    'title': _('Django Documentation'),
                    'url': 'https://docs.djangoproject.com/en/1.7/',
                    'external': True,
                },
                {
                    'title': _('Green Tea Documentation'),
                    'url': 'http://green-tea.readthedocs.io/en/latest/',
                    'external': True,
                },
            ]
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            collapsible=False,
            column=3,
        ))

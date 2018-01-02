from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ReportConfig(AppConfig):
    label = 'report'
    name = 'apps.report'
    verbose_name = _('Report')

    def ready(self):
        from . import receivers # noqa
        # loading plugins...
        # FIXME - maby better to create new model - plugins
        import plugins #noqa
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.views.decorators.cache import cache_page

import apps.api.urls
from apps.core.views import (HomePageView, JobDetailView, JobHistoryView,
                             JobsDiffView, JobsListView, TestDetailView,
                             TestsListView)
from apps.kerberos.views import LoginView
from apps.report.views import ReportListView

admin.autodiscover()

CACHE = 0

urlpatterns = patterns('',
                       url(r'^xml/(?P<id>[0-9]+)$',
                           'apps.core.views.to_xml', name='beaker-xml'),
                       url(r'^import/$', 'apps.core.views.import_xml',
                           name='import-xml'),
                       url(r'^import/group$',
                           'apps.core.views.import_group', name='import-group'),
                       url(r'^api/', include(apps.api.urls)),
                       #   url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^tests/(?P<email>.+)$',
                           TestsListView.as_view(), name='tests-email'),
                       url(r'^reports/$',
                           ReportListView.as_view(), name='reports'),
                       url(r'^accounts/login',
                           LoginView.as_view(), name="login"),
                       url(r'^job/(?P<id>[0-9]+)$',
                           cache_page(60 * CACHE)(JobDetailView.as_view()), name='job-detail'),
                       url(r'^job_history/(?P<id>[0-9]+)$',
                           JobHistoryView.as_view(), name='job-history'),
                       url(r'^test/(?P<id>[0-9]+)$',
                           TestDetailView.as_view(), name='test-detail'),
                       url(r'^(Automation/)?[tT]ests.html$',
                           cache_page(60 * CACHE)(TestsListView.as_view()), name='tests-list'),
                       url(r'^(Automation/)?[jJ]obs.html$',
                           cache_page(60 * CACHE)(JobsListView.as_view()), name='jobs-list'),
                       url(r'^(Automation/)?[dD]iffs.html$',
                           JobsDiffView.as_view(), name='jobs-diff'),
                       url(r'^(Automation/?)?$',
                           HomePageView.as_view(), name='homepage'),

                       url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
                           'django.views.static.serve',
                           {"document_root": settings.MEDIA_ROOT}),

                       url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:],
                           'django.views.static.serve',
                           {"document_root": settings.STATIC_ROOT}),

                       url(r'^admin/doc/', include(
                           'django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^admin/grappelli/', include('grappelli.urls')),
                       )

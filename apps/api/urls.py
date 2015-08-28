#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 1.3.2015


from django.conf.urls import patterns, url

from apps.core.views import ApiView

urlpatterns = patterns('',
                       url(r'^$', 'apps.api.views.performance',
                           name='performance'),
                       url(r'^(?P<action>[^/]+)$',
                           ApiView.as_view(), name='api'),
                       )

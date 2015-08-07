#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 1.3.2015

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin

from apps.core.views import *
from apps.kerberos.views import *

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^', 'apps.api.views.performance',
                           name='performance'),
                       url(r'^(?P<action>[^/]+)$',
                           ApiView.as_view(), name='api'),
                       )

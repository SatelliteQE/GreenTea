#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 1.3.2015

from django.conf.urls import patterns, url, include
from apps.core.views import ApiView
from rest_framework import routers
import views

router = routers.DefaultRouter()
router.register(r'recipe', views.RecipeViewSet)
router.register(r'jobtemplate', views.JobTemplateViewSet)

urlpatterns = patterns('',
                       url(r'^v1/', include(router.urls)),
                       url(r'^$', 'apps.api.views.performance',
                           name='performance'),
                       url(r'^(?P<action>[^/]+)$',
                           ApiView.as_view(), name='api'),
                       )

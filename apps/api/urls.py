#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 1.3.2015

from django.conf.urls import include, patterns, url
from rest_framework import routers

import views
from apps.core.views import ApiView

router = routers.DefaultRouter()
router.register(r'author', views.AuthorViewSet)
router.register(r'jobtemplate', views.JobTemplateViewSet)
router.register(r'recipe', views.RecipeViewSet)
router.register(r'task', views.TaskViewSet)


urlpatterns = patterns('',
                       url(r'^v1/', include(router.urls)),
                       url(r'^$', 'apps.api.views.performance',
                           name='performance'),
                       url(r'^(?P<action>[^/]+)$',
                           ApiView.as_view(), name='api'),
                       )

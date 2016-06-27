#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 1.3.2015

from django.conf.urls import include, patterns, url
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'author', views.AuthorViewSet)
router.register(r'jobtemplate', views.JobTemplateViewSet)
router.register(r'recipe', views.RecipeViewSet)
router.register(r'task', views.TaskViewSet)
router.register(r'arch', views.ArchViewSet)
router.register(r'distro', views.DistroViewSet)
router.register(r'system', views.SystemViewSet)
router.register(r'comment', views.CommentViewSet)
router.register(r'test', views.TestViewSet)


urlpatterns = patterns('',
                       url(r'^v1/', include(router.urls)),
                       url(r'^$', 'apps.api.views.performance',
                           name='performance')
                       )

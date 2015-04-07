#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

import os
import sys
import re
import git
import urllib2
import xml.dom.minidom
from datetime import datetime, timedelta
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.conf import settings

from apps.core.models import *
from apps.core.utils.beaker_import import *


class Command(BaseCommand):
    help = ("Schedule jobs to beaker")
    requires_model_validation = True
    can_import_settings = True

    option_list = BaseCommand.option_list + (
        make_option('--files',
                    dest='files',
                    help='Create template from xml'),
        make_option('--jobs',
                    dest='jobs',
                    help='Create template from jobs'),
        make_option('--position',
                    dest='position',
                    help='Set position of this template'),
    )

    def handle(self, *args, **kwargs):
        init(*args, **kwargs)


def init(*args, **kwargs):
    cfg_jobs, cfg_files = [], []
    if kwargs["jobs"]:
        cfg_jobs = kwargs["jobs"].split(" ")

    if kwargs["files"]:
        cfg_files = kwargs["files"].split(" ")

    for file in cfg_files:
        s = Parser(file=file)
        s.run(position=kwargs["position"])

    for it in cfg_jobs:

        job = Job.objects.get(uid=it)
        recipes = Recipe.objects.filter(job=job)
        for it in recipes:
            distro, status = DistroTemplate.objects.get_or_create(
                name=it.distro.name)

            distro.save()
            recipe = RecipeTemplate(
                jobtemplate=job.template,
                        name=it.whiteboard,
                        distro=distro
            )
            recipe.save()
            for task in Task.objects.filter(recipe=it):
                new_task = TaskTemplate(
                    test=task.test,
                        recipe=recipe,
                )
                new_task.save()

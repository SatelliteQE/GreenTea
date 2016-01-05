#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

from optparse import make_option

from django.core.management.base import BaseCommand

from apps.core.models import (DistroTemplate, Job, Recipe, RecipeTemplate,
                              Task, TaskTemplate)
from apps.core.utils.beaker_import import Parser


class Command(BaseCommand):
    help = ("Schedule jobs to beaker")
    requires_system_checks = True
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

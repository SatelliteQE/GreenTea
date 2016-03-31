#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Year: 2015

from django.dispatch import receiver

from apps.core.signals import recipe_changed, recipe_finished


@receiver(recipe_finished)
def handle_recipe_finished(sender, **kwargs):
    if sender:
        recipe = kwargs.get("recipe")
        print "finished:", sender, recipe


@receiver(recipe_changed)
def handle_recipe_update(sender, **kwargs):
    if sender:
        recipe = kwargs.get("recipe")
        print "update:", sender, recipe

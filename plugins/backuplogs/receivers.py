#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Year: 2015

import logging
import os
import re
from urlparse import urlparse

from django.dispatch import receiver

from apps.core.models import FileLog, Task
from apps.core.signals import recipe_changed, recipe_finished
from apps.core.utils.beaker import Beaker

logger = logging.getLogger(__name__)

backuplogs = ("TESTOUT.log", "journal.xml",
              "install.log", "list-of-packages.txt")


def download_files_from_recipe(recipe):
    """
    function download log files from beaker by global filter 'backuplogs'

    @param object(Recipe)  download selected files from this recipe

    @return None
    """
    b = Beaker()
    listurls = b.listLogs("R:%d" % int(recipe.uid))
    for url in listurls:
        namefile = os.path.basename(urlparse(url).path)
        if namefile in backuplogs:
            logfile, created = FileLog.objects.get_or_create(
                url=url, recipe=recipe)
            if created:
                logfile.save()


@receiver(recipe_finished)
def handle_recipe_finished(sender, **kwargs):
    if sender:
        recipe = kwargs.get("recipe")
        download_files_from_recipe(recipe)
        logger.debug("Download recipe log %s from %s" % (recipe, sender))

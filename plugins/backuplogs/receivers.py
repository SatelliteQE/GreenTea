#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Year: 2015

import logging
import re
import os
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

    @param object(Recipe)  download all files from this recipe

    @return None
    """
    b = Beaker()
    listurls = b.listLogs("R:%d" % int(recipe.uid))
    for url in listurls:
        namefile = os.path.basename(urlparse(url).path)
        if namefile in backuplogs:
            logpath = b.downloadLog(url)
            if not logpath:
                # if file is not download then skip and not save object
                continue
            logfile = FileLog(path=logpath, recipe=recipe)
            logfile.save()

@receiver(recipe_finished)
def handle_recipe_finished(sender, **kwargs):
    if sender:
        recipe = kwargs.get("recipe")
        download_files_from_recipe(recipe)
        logger.debug("Download recipe log %s from %s" % (recipe, sender))

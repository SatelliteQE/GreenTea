#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Year: 2015

import re
import logging
from django.dispatch import receiver
from apps.core.utils.beaker import Beaker
from apps.core.models import FileLog, Task
from apps.core.signals import recipe_changed, recipe_finished

logger = logging.getLogger(__name__)

backuplogs = ("TESTOUT.log", "journal.xml",
              "install.log", "list-of-packages.txt")


@receiver(recipe_finished)
def handle_recipe_finished(sender, **kwargs):
    if sender:
        recipe = kwargs.get("recipe")
        b = Beaker()
        listurls = b.listLogs("R:%d" % int(recipe.uid))
        for url in listurls:
            if len([it for it in backuplogs if url.endswith(it)]) > 0:
                logpath = b.downloadLog(url)
                if not logpath:
                    continue
                logfile = FileLog(path=logpath, recipe=recipe)
                logfile.save()

        logger.debug("Download recipe log %s from %s" % (recipe, sender))

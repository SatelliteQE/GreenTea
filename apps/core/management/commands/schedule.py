#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 20.07.2014

import logging
import time
from optparse import make_option

from django.core.management.base import BaseCommand

from apps.core.models import JobTemplate
from apps.core.utils.beaker import Beaker
from apps.taskomatic.models import TaskPeriodSchedule

logger = logging.getLogger("main")


class Command(BaseCommand):
    help = ("Schedule jobs to beaker")
    requires_system_checks = True
    can_import_settings = True

    option_list = BaseCommand.option_list + (
        make_option('--files',
                    dest='files',
                    help='Schedule jobs from xml files'),
        make_option('--all',
                    action='store_true',
                    dest='all',
                    default=False,
                    help='Schedule all jobs'),
        make_option('--ids',
                    dest='ids',
                    help='Schedule only this JobTemplates.'),
        make_option('--daily',
                    action='store_true',
                    dest='daily',
                    default=False,
                    help='Schedule daily jobs'),
        make_option('--weekly',
                    action='store_true',
                    dest='weekly',
                    default=False,
                    help='Schedule weekly jobs'),
        make_option('--tags',
                    dest='tags',
                    default=False,
                    help='Filter schedule job by template tags'),
    )

    def handle(self, *args, **kwargs):
        bk = Beaker()
        label = None

        filter = dict()
        if "ids" in kwargs and kwargs["ids"]:
            for it in kwargs["ids"].split():
                jobTs = JobTemplate.objects.filter(id=int(it))
                if len(jobTs) == 0:
                    logger.error("This JobTemplate (%s) does not exist." % it)
                    continue
                bk.jobSchedule(jobTs[0])
                # Beaker guys told us we are causing too big load,
                # so adding this sleep
                # FIXME only temporary, rewrite code for scheduling to tttt
                # taskomatic
                time.sleep(4.5)
        if "files" in kwargs and kwargs["files"]:
            cfg_files = kwargs["files"].split()
            if len(cfg_files) == 0:
                logger.error("Missing XmlFile.")
                return False
            for xmlfile in cfg_files:
                print bk.scheduleFromXmlFile(xmlfile)
        if "daily" in kwargs and kwargs["daily"]:
            label = "daily-automation"
            filter["period"] = JobTemplate.DAILY
        if "weekly" in kwargs and kwargs["weekly"]:
            label = "weekly-automation"
            filter["period"] = JobTemplate.WEEKLY
        if "tags" in kwargs and kwargs["tags"]:
            filter["tags__name__in"] = kwargs["tags"].split()
        if "all" in kwargs or len(filter) > 0:
            filter["is_enable"] = True
            jobTs = JobTemplate.objects.filter(**filter).distinct()
            # set schedule period run
            try:
                count = TaskPeriodSchedule.objects.filter(title=label).count()
                schedule = TaskPeriodSchedule.objects.get(
                    title=label, counter=count)
            except TaskPeriodSchedule.DoesNotExist:
                schedule = TaskPeriodSchedule.objects.create(
                    title=label,
                    counter=count,
                )

            logger.info("%s JobTemplates are prepared by schedule %s." %
                        (len(jobTs), schedule))
            for jobT in jobTs:
                job = bk.jobSchedule(jobT, simulate=True)
                logger.info("Job is created: %s" % job)
                if schedule:
                    job.schedule = schedule
                    job.save()
                # Beaker guys told us we are causing too big load,
                # so adding this sleep
                # FIXME only temporary, rewrite code for scheduling to tttt
                # taskomatic
                time.sleep(45)
                return

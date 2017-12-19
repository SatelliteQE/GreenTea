#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import CheckProgress, Job
from apps.core.utils.beaker import Beaker
from apps.core.utils.date_helpers import currentDate

logger = logging.getLogger("backend")

class Command(BaseCommand):
    help = ("Load data from beaker and save to db")
    requires_system_checks = True
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('--running',
                    action='store_true',
                    dest='running',
                    default=False,
                    help='check only running script (only from db) ')
        parser.add_argument('--init',
                    action='store_true',
                    dest='init',
                    default=False,
                    help='init data from beaker and save to db')
        parser.add_argument('--quiet',
                    action='store_true',
                    dest='quiet',
                    default=False,
                    help='quiet mode')
        parser.add_argument('--min-id',
                    dest='minid',
                    help='minimum jobid in filter (optimize communication with beaker)')
        parser.add_argument('--jobs',
                    dest='jobs',
                    help='check concrete jobs, for example: J:12345 J:12346')
        parser.add_argument('--default-date',
                    dest='date',
                    help='Set default date when job was started')
        parser.add_argument('--force',
                    action='store_true',
                    dest='force',
                    default=False,
                    help='skip checking running instance' )


    def handle(self, *args, **kwargs):
        # print "args:", kwargs
        init(*args, **kwargs)


def init(*args, **kwargs):
    if not kwargs["force"] and CheckProgress.IsRunning():
        logger.warning("Process check beaker's jobs is still running... ")
        return
    if kwargs["force"]:
        logger.info("Finish running checks by --force")
        CheckProgress.Restore()

    CheckProgress.Clean()
    progress = CheckProgress()
    bkr = Beaker()

    cfg_running = kwargs["running"]
    cfg_init = kwargs["init"]
    cfg_minid = kwargs["minid"]
    cfg_date = kwargs["date"]
    cfg_quiet = kwargs["quiet"]

    if cfg_date:
        cfg_date = datetime.strptime(kwargs["date"], "%Y-%m-%d")

    if kwargs["jobs"]:
        jobslist = kwargs["jobs"].split(" ")
    elif cfg_init:
        bkr_filter = {"owner": settings.BEAKER_OWNER}
        if cfg_minid:
            bkr_filter["minid"] = kwargs["minid"]
        else:
            # find job from previous init (date) - checked only new jobs
            # datetime.today().date()
            minid = Job.objects.values("uid").filter(
                date__lt=(currentDate() - timedelta(days=2))).order_by("-uid")[:1]
            if minid:
                bkr_filter["minid"] = minid[0]["uid"][2:]
        jobslist = bkr.listJobs(bkr_filter)
    else:
        jobslist = [it["uid"]
                    for it in Job.objects.values("uid").filter(is_finished=False)]

    progress.totalsum = len(jobslist)
    progress.save()
    for it in jobslist:
        if not cfg_quiet:
            logger.info(
                "%d/%d (%s)" %
                (progress.actual, progress.totalsum, it))

        bkr.parse_job(it, running=cfg_running, date_created=cfg_date)
        progress.counter()
    progress.finished()

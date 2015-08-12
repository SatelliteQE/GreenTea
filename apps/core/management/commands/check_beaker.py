#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

import os
import re
import sys
import time
import xml.dom.minidom
import xmlrpclib
import logging
from datetime import datetime, timedelta
from optparse import make_option
from apps.core.models import CheckProgress, Job

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from apps.core.utils.beaker import Beaker
from apps.core.utils.date_helpers import currentDate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ("Load data from beaker and save to db")
    requires_model_validation = True
    can_import_settings = True

    option_list = BaseCommand.option_list + (
        make_option('--running',
                    action='store_true',
                    dest='running',
                    default=False,
                    help='check only running script (only from db) '),
        make_option('--init',
                    action='store_true',
                    dest='init',
                    default=False,
                    help='init data from beaker and save to db'),
        make_option('--quiet',
                    action='store_true',
                    dest='quiet',
                    default=False,
                    help='quiet mode'),
        make_option('--min-id',
                    dest='minid',
                    help='minimum jobid in filter (optimize communication with beaker)'),
        make_option('--jobs',
                    dest='jobs',
                    help='check concrete jobs, for example: J:12345 J:12346'),
        make_option('--default-date',
                    dest='date',
                    help='Set default date when job was started'),
    )

    def handle(self, *args, **kwargs):
        # print "args:", kwargs
        init(*args, **kwargs)


def init(*args, **kwargs):
    progress = CheckProgress()

    cfg_running = kwargs["running"]
    cfg_init = kwargs["init"]
    cfg_minid = kwargs["minid"]
    cfg_date = kwargs["date"]
    cfg_quiet = kwargs["quiet"]
    if kwargs["jobs"]:
        cfg_jobs = kwargs["jobs"].split(" ")
    else:
        cfg_jobs = None

    if cfg_date:
        cfg_date = datetime.strptime(kwargs["date"], "%Y-%m-%d")

    if cfg_init:
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
    if cfg_jobs:
        jobslist = cfg_jobs
    elif cfg_init:
        jobslist = client.jobs.filter(bkr_filter)
    else:
        jobslist = [it["uid"]
                    for it in Job.objects.values("uid").filter(is_finished=False)]

    progress.totalsum = len(jobslist)
    progress.save()
    bkr = Beaker()
    for it in jobslist:
        if not cfg_quiet:
            logger.info(
                "%d/%d (%s)" %
                (progress.actual, progress.totalsum, it))

        bkr.parse_job(it, running=cfg_running, created_date=cfg_date)
        progress.counter()
    progress.finished()

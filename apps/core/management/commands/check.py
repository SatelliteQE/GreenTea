#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

import xmlrpclib
import os
import sys
import re
import time
import xml.dom.minidom
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.conf import settings
from apps.core.models import *
from apps.core.utils.beaker import *
from apps.core.utils.date_helpers import currentDate
from datetime import datetime, timedelta
from optparse import make_option

logger = logging.getLogger(__name__)

if sys.version_info >= (2, 7, 9):
    import ssl

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
    if settings.BEAKER_SERVER.startswith("http"):
        server_url =  "%s/RPC2" % settings.BEAKER_SERVER
    else:
        server_url = "https://%s/RPC2" % settings.BEAKER_SERVER

    client = xmlrpclib.Server(server_url, verbose=0)
    if server_url.startswith("https"):
        # workaround ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
        # certificate verify failed (_ssl.c:590)
        if sys.version_info >= (2, 7, 9):
            client = xmlrpclib.Server(server_url, verbose=0,
                                  context=ssl._create_unverified_context())

    # key = client.auth.login_password(USER, PASS)
    # key = client.auth.login_krb(USER, PASS)

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

    for it in jobslist:
        if not cfg_quiet:
            print("%d/%d (%s)" % (progress.actual, progress.totalsum, it))

        data = client.taskactions.task_info(it)

        # workaround for test which set label with actial date
        labeldates = re.findall(
            r"^([0-9]{4}-[0-9]{2}-[0-9]{2})", data["method"])
        if labeldates:
            label = data["method"][11:]
            # if not cfg_date:
            #    cfg_date = datetime.strptime(labeldates[0],"%Y-%m-%d")
        else:
            label = data["method"]
        jt, status = JobTemplate.objects.get_or_create(whiteboard=label)
        if status:
            jt.save()

        defaults = {"template": jt}
        if cfg_date:
            defaults["date"] = cfg_date
        job, status = Job.objects.get_or_create(uid=it, defaults=defaults)
        job.template = jt
        job.is_running = not data["is_finished"]

        if ((cfg_running and job.is_running) or not job.is_finished):
            content = client.taskactions.to_xml(it)
            dom = xml.dom.minidom.parseString(content)

            for recipexml in dom.getElementsByTagName("recipe"):
                parse_recipe(recipexml, job)

        if not job.is_running:
            job.is_finished = True
        job.save()
        progress.counter()
    progress.finished()

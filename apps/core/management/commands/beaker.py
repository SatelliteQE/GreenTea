#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 20.07.2014

import logging
import time
from datetime import datetime
from optparse import make_option

from texttable import Texttable

from apps.core.models import Job, JobTemplate, Recipe
from apps.core.utils.advance_command import AdvancedCommand, make_option_group
from apps.core.utils.beaker import Beaker
from apps.taskomatic.models import TaskPeriod, TaskPeriodSchedule

logger = logging.getLogger("main")

from django.core.management.base import BaseCommand, CommandError


class BeakerCommand():

    def __init__(self):
        self.beaker = Beaker()

    def cancel(self, *argvs, **kwargs):
        logger.warning("not implemented")

    def schedule(self, label="default", *argvs, **kwargs):
        simulate = kwargs.get("simulate")
        reserver = kwargs.get("reserve")
        fullInfo = kwargs.get("fullInfo")

        if kwargs.get("list"):
            tp = TaskPeriod.objects.all()
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.header(["Id", "Title", "Label", "Schedule"])
            for it in tp:
                table.add_row([it.id, it.title, it.label, it.cron])
            print(table.draw())

        if kwargs.get("template_id"):
            template_ids = kwargs.get("template_id")
            logger.debug("Schedule template id %s" % template_ids)

            filter = {"id__in": template_ids}
            self.scheduleByJobTemplates(
                filter, label, fullInfo, simulate, reserver)

        if kwargs.get("period_label"):
            period_label = kwargs.get("period_label")
            filter = {"schedule__label__in": period_label, "is_enable": True}
            if not label:
                label = period_label
            self.scheduleByJobTemplates(
                filter, "".join(label), fullInfo, simulate, reserver)

    def scheduleByJobTemplates(self, filter, label, fullInfo, simulate, reserve):
        jobTs = JobTemplate.objects.filter(**filter).distinct()
        logger.info("%s JobTemplates are prepared." % len(jobTs))
        if fullInfo:
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.header(["Job", "Whiteboard", "Tags"])
        # do not create TaskPeriodSchedule when there are no jobs to schedule
        if len(jobTs) == 0:
            logger.info("No jobs for TaskPeriod %s" % label)
            return

        period = TaskPeriod.objects.get(label=label)
        count = TaskPeriodSchedule.objects.filter(period=period).count()
        schedule = TaskPeriodSchedule.objects.create(
            title=label,
            period=period,
            counter=count,
        )

        for jobT in jobTs:
            job = ""
            if not simulate:
                job = self.beaker.jobSchedule(jobT, reserve)
                if job:
                    job.schedule = schedule
                    job.save()
                    logger.info("%s job was successful scheduled."
                                % job.uid)
                else:
                    logger.info("Problem with scheduling of job template (%s)."
                                % jobT.id)
            if fullInfo:
                tags = ",".join([tag.name for tag in jobT.tags.all()])
                table.add_row([str(job), jobT.whiteboard, tags])
            if not simulate:
                # Beaker guys told us we are causing too big load,
                # so adding this sleep
                # FIXME only temporary, rewrite code for scheduling to tttt
                # taskomatic
                time.sleep(4.5)
        if fullInfo:
            print table.draw()


class Command(BaseCommand):
    help = "Command for run beaker client"
    can_import_settings = True

    def add_arguments(self, parser):
        # options
        parser.add_argument('--simulate', action='store_true',
                            help='Simulate action, use it with --fullinfo.',
                            default=False)
        parser.add_argument('--reserve', action='store_true',
                            default=False)
        parser.add_argument('--fullinfo', action='store_true',
                            help='Show more informations.',
                            default=False)

        group = parser.add_argument_group("schedule")
        group.add_argument('--template_id', nargs='+', type=int,
                           help='Schedule only job templates, which are required. We '
                           'can use more values, which are separated by comma.')
        group.add_argument('--template_file', nargs='+', type=str)
        group.add_argument('--period_label', nargs='+', type=str)
        group.add_argument('--label', nargs=None, type=str)
        group.add_argument('--list', action='store_true', default=False)

        group = parser.add_argument_group("cancel")
        group.add_argument('--job_id', nargs='+', type=str,)

#        group = parser.add_argument_group("reschedule")
#        group.add_argument('--job_id', nargs='+', type=str, )

#        group = parser.add_argument_group("return2beaker")
#        group.add_argument('--job_id', nargs='+', type=str,)

        parser.add_argument('action', choices=("schedule", "reschedule", "cancel"),
                            help='Action for beaker client')

    def handle(self, *args, **options):
        action = options["action"]

        bk = BeakerCommand()
        fce = getattr(bk, action)
        fce(**options)
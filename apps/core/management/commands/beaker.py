#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 20.07.2014

import logging
import time

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max, Count
from texttable import Texttable

from apps.core.models import Job, JobTemplate, Recipe, FileLog
from apps.core.utils.beaker import Beaker
from apps.taskomatic.models import TaskPeriod, TaskPeriodSchedule
from django.conf import settings

logger = logging.getLogger("backend")


class BeakerCommand():

    def __init__(self):
        self.beaker = Beaker()

    def return2beaker(self, return2beaker_recipe, *argvs, **kwargs):
        if not return2beaker_recipe:
            raise CommandError(
                "return2beaker - parameter return2beaker_recipe cannot be empty")

        for uid in return2beaker_recipe:
            recipe = Recipe.objects.get(uid=uid[2:])
            res = self.beaker.return2beaker(recipe)
            if res:
                logger.info("R:%s recipes was returned to beaker."
                            % recipe.uid)
            else:
                logger.info("Problem with returning to beaker (R:%s)."
                            % recipe.uid)
            self.beaker.systemRelease(recipe)

    def reschedule(self, reschedule_job, *argvs, **kwargs):
        if not reschedule_job:
            raise CommandError(
                "reschedule - parameter reschedule_job cannot be empty")

        message = kwargs.get("reschedule-message")
        for uid in reschedule_job:
            job = Job.objects.get(uid=uid)
            job_new = self.beaker.jobReschedule(job, message)
            if job_new:
                logger.info("%s job was rescheduled as %s."
                            % (job.uid, job_new.uid))
            else:
                logger.info("Problem with rescheduling of job (%s)."
                            % job.uid)

    def cancel(self, cancel_job, *argvs, **kwargs):
        if not cancel_job:
            raise CommandError("cancel - parameter cancel_job cannot be empty")

        message = kwargs.get("cancel-message")
        for uid in cancel_job:
            job = Job.objects.get(uid=uid)
            res = self.beaker.jobCancel(job, message)
            if res:
                logger.info("%s job was cancled." % job.uid)
            else:
                logger.info("Problem with canceling of job (%s)." % job.uid)

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

        if kwargs.get("schedule_label"):
            period_label = kwargs.get("schedule_label")
            filter = {"schedule__label__in": period_label, "is_enable": True}
            if not label:
                label = period_label
            self.scheduleByJobTemplates(
                filter, "".join(label), fullInfo, simulate, reserver)

    def checklogs(self, **kwargs):
        logger.info("%d files to download" % FileLog.objects.filter(status_code=0).count())
        logger.info("%d files to indexing" % FileLog.objects.filter(is_indexed=False, is_downloaded=True).count())
        logger.info("status: %s" % FileLog.objects.values("status_code").annotate(counter=Count("status_code")))

        b = Beaker()
        for it in FileLog.objects.filter(status_code=0)\
                         .order_by("-created")[0:settings.MAX_LOGS_IN_ONE_CHECK]:
            it.status_code, logpath = b.downloadLog(it.url)
            if not logpath:
                # if file is not download then skip and not save object
                it.save()
                continue
            it.path = logpath
            it.is_downloaded = True
            it.save()
            try:
                it.parse_journal()
            except Exception as e:
                logger.debug("parse log file: %s" % e)

        if settings.ELASTICSEARCH:
            for it in FileLog.objects.filter(is_downloaded=True, is_indexed=False)\
                            .order_by("-created")[0:settings.MAX_LOGS_IN_ONE_CHECK]:
                try:
                    it.index()
                except Exception as e:
                    logger.info("indexing %s: %s" % (it.path, e))

        FileLog.clean_old()

    def scheduleByJobTemplates(
            self, filter, label, fullInfo, simulate, reserve):
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
        count = TaskPeriodSchedule.objects.filter(
            period=period).aggregate(Max('counter')).get("counter__max")

        schedule = TaskPeriodSchedule.objects.create(
            title=label,
            period=period,
            counter=count + 1 if count is not None else 0,
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
        group.add_argument('--template-id', nargs='+', type=int,
                           help='Schedule only job templates, which are required. We '
                           'can use more values, which are separated by comma.')
        group.add_argument('--template-file', nargs='+', type=str)
        group.add_argument('--schedule-label', nargs='+', type=str)
        group.add_argument('--label', nargs=None, type=str)
        group.add_argument('--list', action='store_true', default=False)

        group = parser.add_argument_group("cancel")
        group.add_argument('--cancel-job', nargs='+', type=str,
                           help='Cancel only jobs, which are scheduled from required'
                           'job templates. We can use more values')
        group.add_argument('--cancel-message', nargs=None, type=str)

        group = parser.add_argument_group("reschedule")
        group.add_argument('--reschedule-job', nargs='+', type=str,
                           help='Reschedule only jobs, which are required. Use UID'
                           '(J:12345) for identify of job. We can use more values.')
        group.add_argument('--reschedule-message', nargs=None, type=str)

        group = parser.add_argument_group("return2beaker")
        group.add_argument('--return2beaker-recipe', nargs='+', type=str,
                           help='Return2beaker only jobs, which are required. Use UID'
                           '(J:12345) for identify of job. We can use more values')
        group.add_argument('--return2beaker-message', nargs=None, type=str,)

        parser.add_argument('action', choices=("schedule", "reschedule", "return2beaker", "cancel", "checklogs"),
                            help='Action for beaker client')

    def handle(self, *args, **options):
        action = options["action"]

        bk = BeakerCommand()
        fce = getattr(bk, action)
        fce(**options)

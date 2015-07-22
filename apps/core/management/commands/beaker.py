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
from apps.taskomatic.models import TaskPeriodSchedule

logger = logging.getLogger(__name__)


class Command(AdvancedCommand):
    requires_model_validation = True
    can_import_settings = True
    schedule = None

    option_list = AdvancedCommand.option_list + (
        make_option('--info',
                    action='store_true',
                    dest='info',
                    default=False,
                    help='Show more informations.'),
                make_option('--simulate',
                            action='store_true',
                            dest='simulate',
                            default=False,
                            help='Simulate action, use it with --fullinfo.'),
                make_option('--label',
                            dest='label',
                            default=False,
                            help='Name of schedule label'),
    )
    option_groups = (
        # SCHEDULE
         make_option_group(
             'Options for schedule',
            description='Options for scheduling of jobs in beaker',
            option_list=(
                make_option('--schedule-all',
                            action='store_true',
                            dest='all',
                            default=False,
                            help='Schedule all active job templates'),
                make_option('--schedule-daily',
                            action='store_true',
                            dest='daily',
                            default=False,
                            help='Schedule daily job templates'),
                make_option('--schedule-weekly',
                            action='store_true',
                            dest='weekly',
                            default=False,
                            help='Schedule weekly job templates'),
                make_option('--schedule-template',
                            dest='template',
                            help='Schedule only job templates, which are required. We '
                            'can use more values, which are separated by comma.'),
                make_option('--schedule-tags',
                            dest='tags',
                            default=False,
                            help='Schedule job templates, which have required tags.'
                            'We can use more values, separated by comma'),
                make_option('--schedule-reservsys',
                            action='store_true',
                            dest='reservsys',
                            default=False,
                            help='Adding forcibly of the reservsys task into new job.'),
                make_option('--schedule_id',
                            dest='schedule_id',
                            default=False,
                            help='Set period schedule run'),
            ),
         ),
        # RESCHEDULE
         make_option_group(
             'Options for reschedule',
            description='Options for rescheduling of jobs',
            option_list=(
                make_option('--reschedule-all',
                            action='store_true',
                            dest='all',
                            default=False,
                            help='Reschedule all active jobs'),
                make_option('--reschedule-daily',
                            action='store_true',
                            dest='daily',
                            default=False,
                            help='Reschedule daily job'),
                make_option('--reschedule-weekly',
                            action='store_true',
                            dest='weekly',
                            default=False,
                            help='Reschedule weekly jobs'),
                make_option('--reschedule-job',
                            dest='job',
                            help='Reschedule only jobs, which are required. Use UID '
                            '(J:12345) for identify of job. We can use more '
                            'values, which are separated by comma.'),
                make_option('--reschedule-template',
                            dest='template',
                            help='Reschedule only jobs, which are required. We '
                            'can use more values, which are separated by comma.'),
                make_option('--reschedule-tags',
                            dest='tags',
                            default=False,
                            help='Reschedule jobs, which have required tags.'
                            'We can use more values, separated by comma'),
                make_option('--reschedule-message',
                            dest='message',
                            default="",
                            help='The comment for rescheduling of jobs.'),
            ),
         ),
        # RETURN2BEAKER
         make_option_group(
             'Options for return2beaker',
            description='Options for return2beaker of jobs',
            option_list=(
                make_option('--return2beaker-all',
                            action='store_true',
                            dest='all',
                            default=False,
                            help='Return2beaker all active jobs'),
                make_option('--return2beaker-daily',
                            action='store_true',
                            dest='daily',
                            default=False,
                            help='Return2beaker daily jobs'),
                make_option('--return2beaker-weekly',
                            action='store_true',
                            dest='weekly',
                            default=False,
                            help='Return2beaker weekly jobs'),
                make_option('--return2beaker-recipe',
                            dest='recipe',
                            help='Return2beaker only recipes, which are required. Use '
                            'UID (R:12345) for identify of recipe. We can use '
                            'more values, which are separated by comma.'),
                make_option('--return2beaker-job',
                            dest='job',
                            help='Return2beaker only jobs, which are required. Use UID'
                            ' (J:12345) for identify of job. We can use more '
                            'values, which are separated by comma.'),
                make_option('--return2beaker-template',
                            dest='template',
                            help='Return2beaker only jobs, which are required. We '
                            'can use more values, which are separated by comma.'),
                make_option('--return2beaker-tags',
                            dest='tags',
                            default=False,
                            help='Return2beaker jobs, which have required tags.'
                            'We can use more values, separated by comma'),
            ),
         ),
        # CANCEL
        make_option_group(
            'Options for cancel',
            description='Options for canceling of jobs',
            option_list=(
                make_option('--cancel-all',
                            action='store_true',
                            dest='all',
                            default=False,
                            help='Cancel all active jobs'),
                make_option('--cancel-daily',
                            action='store_true',
                            dest='daily',
                            default=False,
                            help='Cancel today daily jobs'),
                make_option('--cancel-weekly',
                            action='store_true',
                            dest='weekly',
                            default=False,
                            help='Cancel weekly jobs'),
                make_option('--cancel-job',
                            dest='job',
                            help='Cancel only jobs, which are required. Use UID '
                            '(J:12345) for identify of job. We can use more '
                            'values, which are separated by comma.'),
                make_option('--cancel-template',
                            dest='template',
                            help='Cancel only jobs, which are scheduled from required '
                            'job templates. We can use more values, which are '
                            'separated by comma.'),
                make_option('--cancel-tags',
                            dest='tags',
                            default=False,
                            help='Cancel jobs, which have required tags.'
                            'We can use more values, separated by comma'),
                make_option('--cancel-message',
                            dest='message',
                            default="",
                            help='The comment for canceling of jobs.'),
            ),
    ),
    )

    def usage(self, subcommand):
        return (" %%prog %s (schedule|reschedule|return2beaker|cancel) "
                "[options]\n\n=== This utility provides functions for playing"
                " with beaker ==\n")\
               % subcommand

    def handle(self, *args, **kwargs):
        if len(args) == 0:
            self.print_help("./manage.py", "beaker")
            return

        self.beaker = Beaker()
        if args[0] == "beaker":
            # web commnand call argv with (u'beaker', u'reschedule')
            action = args[1]
        else:
            # commnand call argv with ('reschedule',)
            action = args[0]

        if action == 'schedule':
            self.__scheduleActions(args, kwargs)
        elif action == 'reschedule':
            self.__rescheduleActions(args, kwargs)
        elif action == 'return2beaker':
            self.__return2beakerActions(args, kwargs)
        elif action == 'cancel':
            self.__cancelActions(args, kwargs)
        else:
            assert("Action %s is not supported" % action)

    #--------------------------------------------------------------------------
    # SCHEDULE
    #--------------------------------------------------------------------------

    def __scheduleActions(self, args, kwargs):
        filter = dict()
        label = kwargs.get("label")
        if kwargs.get("daily"):
            filter["period"] = JobTemplate.DAILY
            label = "daily"
        if kwargs.get("weekly"):
            filter["period"] = JobTemplate.WEEKLY
            label = "weekly"
        if kwargs.get("tags"):
            filter["tags__name__in"] = kwargs.get("tags", "").split(",")
            if len(filter["tags__name__in"]) == 0:
                logger.error("Minimal one tag is required.")
                return False
        if kwargs.get("all") or len(filter) > 0:
            filter["is_enable"] = True
        if kwargs.get("template"):
            filter['id__in'] = kwargs.get("template", "").split(',')
            if len(filter['id__in']) == 0:
                logger.error("Minimal one job template is required.")
                return False
        if kwargs.get("schedule_id"):
            schedule_id = int(kwargs["schedule_id"])
            try:
                self.schedule = TaskPeriodSchedule.objects.get(id=schedule_id)
            except TaskPeriodSchedule.DoesNotExist:
                coutner = len(TaskPeriodSchedule.objects.filter(period=None))
                self.schedule = TaskPeriodSchedule.objects.create(
                        title="%s" % datetime.now(), counter=coutner)
        if len(filter) > 0:
            self.__scheduleTemplates(filter,
                                     label,
                                     kwargs.get("info"),
                                     kwargs.get("simulate"),
                                     kwargs.get("reservsys"))
            return True
        if kwargs.get("files"):
            cfg_files = kwargs["files"].split()
            if len(cfg_files) == 0:
                logger.error("Minimal one XML file is required.")
                return False
            for xmlfile in cfg_files:
                res = self.beaker.scheduleFromXmlFile(xmlfile)
                if not res:
                    logger.error("Problem with schedule '%s' xml file" %
                                 xmlfile)
            return True
        logger.error("Unsupported parameters")
        return False

    def __scheduleTemplates(self, filter, label, fullInfo, simulate, reserve):
        jobTs = JobTemplate.objects.filter(**filter).distinct()
        logger.info("%s JobTemplates are prepared." % len(jobTs))
        if fullInfo:
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.header(["Job", "Whiteboard", "Tags"])

        try:
            count = TaskPeriodSchedule.objects.filter(title=label).count()
            schedule = TaskPeriodSchedule.objects.get(
                title=label, counter=count)
        except TaskPeriodSchedule.DoesNotExist:
            schedule = TaskPeriodSchedule.objects.create(
                title=label,
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

    #--------------------------------------------------------------------------
    # RESCHEDULE
    #--------------------------------------------------------------------------

    def __rescheduleActions(self, args, kwargs):
        filter = dict()
        if kwargs.get("daily"):
            filter["template__period"] = JobTemplate.DAILY
        if kwargs.get("weekly"):
            filter["template__period"] = JobTemplate.WEEKLY
        if kwargs.get("tags"):
            filter["template__tags__name__in"] = kwargs.get("tags", "")\
                                                       .split(",")
            if len(filter["template__tags__name__in"]) == 0:
                logger.error("Minimal one tag is required.")
                return False
        if kwargs.get("template"):
            filter['template__id__in'] = kwargs.get("template", "").split(',')
            if len(filter['template__id__in']) == 0:
                logger.error("Minimal one job template is required.")
                return False
        if kwargs.get("job"):
            # need escaping quotes in string !!
            filter['uid__in'] = kwargs.get(
                "job", "").replace('\'', '').split(',')
            if len(filter['uid__in']) == 0:
                logger.error("Minimal one job is required.")
                return False
        if kwargs.get("all") or len(filter) > 0:
            self.__rescheduleTemplates(filter,
                                     kwargs.get("info"),
                                     kwargs.get("simulate"),
                                     kwargs.get("message"))
            return True
        logger.error("Unsupported parameters")
        return False

    def __rescheduleTemplates(self, filter, fullInfo, simulate, message):
        jobs = Job.objects.filter(**filter).distinct()
        logger.info("%s jobs are prepared to reschedule." % len(jobs))
        if fullInfo:
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.header(["from Job", "to Job", "Whiteboard", "Tags"])
        for job in jobs:
            jobN = ""
            if not simulate:
                jobN = self.beaker.jobReschedule(job, message)
                if jobN:
                    logger.info("%s job was rescheduled as %s."
                                % (job.uid, jobN.uid))
                else:
                    logger.info("Problem with rescheduling of job (%s)."
                                % job.uid)
            if fullInfo:
                tags = ",".join([tag.name for tag in job.template.tags.all()])
                table.add_row([job.uid, str(jobN), job.template.whiteboard,
                               tags])
            else:
                print str(jobN)
            if not simulate:
                # Beaker guys told us we are causing too big load,
                # so adding this sleep
                # FIXME only temporary, rewrite code for scheduling to tttt
                # taskomatic
                time.sleep(4.5)
        if fullInfo:
            print table.draw()

    #--------------------------------------------------------------------------
    # RETURN2BEAKER
    #--------------------------------------------------------------------------

    def __return2beakerActions(self, args, kwargs):
        filter = dict()
        if kwargs.get("daily"):
            filter["job__template__period"] = JobTemplate.DAILY
        if kwargs.get("weekly"):
            filter["job__template__period"] = JobTemplate.WEEKLY
        if kwargs.get("tags"):
            filter["job__template__tags__name__in"] = kwargs.get("tags", "")\
                                                            .split(",")
            if len(filter["job__template__tags__name__in"]) == 0:
                logger.error("Minimal one tag is required.")
                return False
        if kwargs.get("template"):
            filter['job__template__id__in'] = kwargs.get("template", "")\
                                                   .split(',')
            if len(filter['job__template__id__in']) == 0:
                logger.error("Minimal one job template is required.")
                return False
        if kwargs.get("job"):
            filter['job__uid__in'] = kwargs.get("job", "").split(',')
            if len(filter['job__uid__in']) == 0:
                logger.error("Minimal one job is required.")
                return False
        if kwargs.get("recipe"):
            filter['uid__in'] = kwargs.get("recipe", "").replace('R:', '')\
                                        .replace("'", "").split(',')
            if len(filter['uid__in']) == 0:
                logger.error("Minimal one recipe is required.")
                return False
        if kwargs.get("all") or len(filter) > 0:
            filter['status'] = Recipe.RUNNING
            self.__return2beakerTemplates(filter,
                                          kwargs.get("info"),
                                          kwargs.get("simulate"))
            return True
        logger.error("Unsupported parameters")
        return False

    def __return2beakerTemplates(self, filter, fullInfo, simulate):
        recipes = Recipe.objects.filter(**filter).distinct()
        logger.info("%s recipes are prepared to return2beaker." % len(recipes))
        if fullInfo:
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.header(["Returned", "Recipe", "Job", "Whiteboard", "Tags"])
        for recipe in recipes:
            res = False
            if not simulate:
                res = self.beaker.return2beaker(recipe)
                if res:
                    logger.info("R:%s recipes was returned to beaker."
                                % recipe.uid)
                else:
                    logger.info("Problem with returning to beaker (R:%s)."
                                % recipe.uid)
            if fullInfo:
                tags = ",".join([tag.name for tag in recipe.job.template
                                                               .tags.all()])
                table.add_row([res, "R:%s" % str(recipe), str(recipe.job),
                               "%s - %s" % (recipe.job.template.whiteboard,
                                            recipe.whiteboard), tags])
            else:
                print str(recipe)
        if fullInfo:
            print table.draw()

    #--------------------------------------------------------------------------
    # CANCEL
    #--------------------------------------------------------------------------

    def __cancelActions(self, args, kwargs):
        filter = dict()
        if kwargs.get("daily"):
            filter["template__period"] = JobTemplate.DAILY
        if kwargs.get("weekly"):
            filter["template__period"] = JobTemplate.WEEKLY
        if kwargs.get("tags"):
            filter["template__tags__name__in"] = kwargs.get("tags", "")\
                                                       .split(",")
            if len(filter["template__tags__name__in"]) == 0:
                logger.error("Minimal one tag is required.")
                return False
        if kwargs.get("template"):
            filter['template__id__in'] = kwargs.get("template", "").split(',')
            if len(filter['template__id__in']) == 0:
                logger.error("Minimal one job template is required.")
                return False
        if kwargs.get("job"):
            filter['uid__in'] = kwargs.get("job", "").split(',')
            if len(filter['uid__in']) == 0:
                logger.error("Minimal one job is required.")
                return False
        if kwargs.get("all") or len(filter) > 0:
            filter['is_finished'] = False
            self.__cancelJobs(filter, kwargs.get("info"),
                              kwargs.get("simulate"), kwargs.get("message"))
            return True
        logger.error("Unsupported parameters")
        return False

    def __cancelJobs(self, filter, fullInfo, simulate, message):
        jobs = Job.objects.filter(**filter).distinct()
        logger.info("You are going to cancel %s jobs " % len(jobs))
        if fullInfo:
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.header(["Canceled", "Job", "Whiteboard", "Tags"])
        for job in jobs:
            res = False
            if not simulate:
                res = self.beaker.jobCancel(job, message)
                if res:
                    logger.info("%s job was cancled." % job.uid)
                else:
                    logger.info("Problem with canceling of job (%s)."
                                % job.uid)
            if fullInfo:
                tags = ",".join([tag.name for tag in job.template.tags.all()])
                table.add_row([str(res), job.uid, job.template.whiteboard,
                               tags])
            if not simulate:
                # Beaker guys told us we are causing too big load,
                # so adding this sleep
                # FIXME only temporary, rewrite code for scheduling to tttt
                # taskomatic
                time.sleep(4.5)
        if fullInfo:
            print table.draw()

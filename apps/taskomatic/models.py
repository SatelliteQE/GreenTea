# -*- coding: utf-8 -*-
# author: Pavel Studenik
# email: pstudeni@redhat.com
# created: 24.1.2014

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 20.07.2014

import re
import sys
import time
import logging
import inspect
import traceback
from croniter import croniter
from datetime import datetime, timedelta
from single_process import single_process
from django.db import models
from django.conf import settings
# from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, handle_default_options
from django.utils.translation import ugettext_lazy as _
from apps.taskomatic.utils.stream2logger import StreamToLogger
from apps.core.utils.date_helpers import TZDateTimeField, toLocalZone


logger = logging.getLogger('commands')
sys.stderr = StreamToLogger(logger, logging.WARN)  # Redirect stderr to logger


class TaskPeriodSchedule(models.Model):
    title = models.CharField(max_length=64)
    period = models.ForeignKey("TaskPeriod", blank=True, null=True)
    date_create = TZDateTimeField(_('Date of create'), default=datetime.now)
    counter = models.BigIntegerField(default=0)

    def __unicode__(self):
        return self.title


class TaskPeriod(models.Model):
    title = models.CharField(max_length=64)
    label = models.CharField(max_length=64, null=True, blank=True)
    common = models.CharField(max_length=128)
    date_last = TZDateTimeField(_('Date of last run'), null=True, blank=True)
    is_enable = models.BooleanField(default=False)
    cron = models.CharField(max_length=64, default="*  *  *  *  *")

    def get_previous_run(self):
        tasks = Task.objects.filter(period=self).order_by("-date_run")
        if len(tasks) > 0:
            return tasks[0].date_run
        return None

    def __unicode__(self):
        return self.title

    def createTask(self):
        res = self.common.split(' ', 1)
        command = res.pop(0)
        params = "" if len(res) == 0 else res.pop()
        label = TaskPeriodSchedule.objects.create(
            title=self.title,
                period=self,
                counter=len(TaskPeriodSchedule.objects.filter(period=self))
        )
        task = Task.objects.create(title=self.title,
                                   common=command,
                                   common_params=params,
                                   status=Task.STATUS_ENUM_WAIT,
                                   period=self)
        return task


class Task(models.Model):
    STATUS_ENUM_WAIT = 0
    STATUS_ENUM_INPROGRESS = 1
    STATUS_ENUM_DONE = 2
    STATUS_ENUM_ERROR = 3
    STATUS_ENUM = (
        (STATUS_ENUM_WAIT, "Waiting"),
       (STATUS_ENUM_INPROGRESS, "In progress"),
       (STATUS_ENUM_DONE, "Done"),
       (STATUS_ENUM_ERROR, "Error"),
    )
    # user = models.ForeignKey(User)
    title = models.CharField(max_length=64)
    common = models.CharField(max_length=128)
    common_params = models.TextField(_('Parameters'), blank=True)
    status = models.IntegerField(default=0, choices=STATUS_ENUM)
    exit_result = models.TextField(_('Result log'), blank=True)
    date_create = TZDateTimeField(_('Date of create'), default=datetime.now)
    date_run = TZDateTimeField(_('Date of pick up'), blank=True, null=True)
    time_long = models.FloatField(default=0.0)  # better set to NULL
    period = models.ForeignKey(TaskPeriod, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_time_long(self):
        t = timedelta(seconds=self.time_long)
        return str(t)

    def get_params(self):
        data = {}
        for it in self.common_params.split():
            key, value = it.strip().split("=")
            data[key] = value
        return data

    def run(self, hook, errorHandler=None):
        t1 = datetime.now()
        self.status = self.STATUS_ENUM_INPROGRESS  # set status "in progress"
        self.save()

        # --- RUN --- #
        if errorHandler:
            errorHandler.flush()
        params = [it.strip() for it in self.common_params.split(' ')]
        try:
            obj = hook()
            parser = obj.create_parser('./manage.py', self.common)
            options, args = parser.parse_args(params)
            handle_default_options(options)
            obj.execute(*args, **options.__dict__)
            self.status = self.STATUS_ENUM_DONE  # set status "done"
        except Exception as e:
            self.exit_result = traceback.format_exc()
            self.status = self.STATUS_ENUM_ERROR  # set status "error"
            logger.exception(e)
        # Get all errors from logger
        if errorHandler:
            for er in errorHandler.flush():
                self.exit_result += er.getMessage() + "\n"
        # --- END RUN --- #
        t0 = datetime.now()
        t2 = t0 - t1
        self.time_long = t2.seconds + t2.microseconds / 1000000.0
        self.date_run = t0
        self.save()


class Taskomatic:
    hooks = None
    logHandler = None

    class ListBufferingHandler(logging.handlers.BufferingHandler):

        def shouldFlush(self, record):
            return False

        def flush(self):
            old = self.buffer
            self.buffer = list()
            return old

    def __getHooksFromModule(self, module):
        for name, obj in inspect.getmembers(module):
            if inspect.ismodule(obj) and\
               obj.__name__.startswith(module.__name__):
                # Load and check submodules
                self.__getHooksFromModule(getattr(module, name))
            if inspect.isclass(obj) and obj.__module__ == module.__name__ and\
               issubclass(obj, BaseCommand):
                # Add class as hook
                commnad_name = re.sub(r".*\.", '', obj.__module__)
                if "COMMAND_NAME" in obj.__dict__:
                    commnad_name = obj.COMMAND_NAME
                self.hooks[commnad_name] = obj

    def __importModule(self, name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    def getHooks(self):
        self.hooks = dict()
        for moduleName in settings.TASKOMATIC_HOOKS:
            self.__getHooksFromModule(self.__importModule(moduleName))
        return self.hooks

    def __checkTaskPeriods(self):
        tPeriods = TaskPeriod.objects.filter(is_enable=True)
        for period in tPeriods:
            if not period.date_last:
                period.date_last = datetime.now()
                period.save()
            last_check = toLocalZone(period.date_last)
            citer = croniter(period.cron, last_check)
            next_date = citer.get_next()
            if next_date < time.time():
                period.createTask()
                period.date_last = datetime.now()
                period.save()

    def __checkTasks(self):
        tasks = Task.objects.filter(status=Task.STATUS_ENUM_WAIT)
        self.logHandler = Taskomatic.ListBufferingHandler(0)
        self.logHandler.setLevel(logging.INFO)
        logger.addHandler(self.logHandler)
        for task in tasks:
            if task.common in self.hooks:
                task.run(self.hooks[task.common], self.logHandler)
            else:
                print "operation '%s' is not supported" % task.common

    def __cleanOldTasks(self):
        # delete old tasks with status DONE, keep only last 300 tasks
        [it.delete() for it in Task.objects
            .filter(status=Task.STATUS_ENUM_DONE).order_by("-date_run")[300:]]

    @single_process
    def run(self):
        self.getHooks()
        self.__checkTaskPeriods()
        self.__checkTasks()
        self.__cleanOldTasks()

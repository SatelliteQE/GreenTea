#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 20.07.2014

import logging
import os
import random
import re
import subprocess
import sys
import urllib2
import xml.dom.minidom
import xmlrpclib
from datetime import datetime, timedelta
from urlparse import urlparse

from django.conf import settings
from django.template import Context, Template
from django.template.defaultfilters import slugify

from apps.core.models import (PASS, RETURNWHENGREEN, Arch, Author, Distro, Job,
                              JobTemplate, Recipe, RecipeTemplate, System,
                              Task, TaskTemplate, Test)

logger = logging.getLogger(__name__)

if sys.version_info >= (2, 7, 9):
    import ssl


def total_sec(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) \
        / 10 ** 6


def strToSec(string):
    data = string.split(" ")
    days = 0
    if len(data) == 3:
        days = int(data[0])
    try:
        t = datetime.strptime(data[-1], "%H:%M:%S")
        delta = timedelta(days=days, hours=t.hour, minutes=t.minute,
                          seconds=t.second)
    except ValueError:
        logger.error("ValueError %s" % data)
        return 0
    if sys.version_info < (2, 7):
        return total_sec(delta)
    else:
        return delta.total_seconds()


class Beaker:

    def __init__(self):
        self.username = getattr(settings, "BEAKER_OWNER")
        self.password = getattr(settings, "BEAKER_PASS")

        self.hub = getattr(settings, "BEAKER_SERVER")
        if not self.hub.startswith("http"):
            self.hub = "https://%s" % self.hub
        self.server_url = "%s/RPC2" % self.hub

    def execute(self, command, param):
        """
            Execute beaker command
        """
        auth = ""
        if self.username:
            auth = "--username='%s' --password='%s'" % (self.username,
                                                        self.password)
        command = "bkr %s %s %s --hub=%s" % (command, param, auth, self.hub)
        logger.debug(command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return p.communicate()

    def jobCancel(self, job, message=""):
        if not isinstance(job, Job) or not job:
            raise Exception("Parameter 'job' is not instance of class Job")
        result = self.execute("job-cancel", "--msg \"%s\" %s" % (message,
                                                                 job.uid))
        if re.search("Cancelled\s+%s" % job.uid, result[0]):
            self.parse_job(job.uid)
            return True
        else:
            logger.error("Problem with canceling of the job (%s). output: '%s'"
                         (job.uid, "\n".join(result)))
            return False

    def jobSchedule(self, jobT, reserve=False, schedule=None):
        if not isinstance(jobT, JobTemplate) or not jobT:
            raise Exception("Parameter 'jobT' is not instance of class "
                            "JobTemplate")
        date = datetime.today().date().isoformat()
        tmp = "beaker_tmp_%s.xml" % random.getrandbits(28)
        path = "%s/%s.xml" % (date, tmp)
        xmlfile, job = None, None
        try:
            xmlfile = self.generateXmlFile(jobT, path, reserve)
            job = self.__jobSchedule(xmlfile, jobT)
        except:
            # FIXME
            # TypeError: argument 1 must be string or read-only character
            # buffer, not None
            logger.error("schedule file %s: %s %s" % (xmlfile, job, jobT))
        if job:
            os.rename(xmlfile, xmlfile.replace(tmp, slugify(job.uid)))
            self.parse_job(job.uid)
        return job

    def jobReschedule(self, job, message):
        self.jobCancel(job, message)
        date = job.date.date().isoformat()
        path = "%s/%s.reschedule.xml" % (date, slugify(job.id))
        # A potential problem with reservesys
        xmlfile = self.generateXmlFile(job.template, path)
        jobNew = self.__jobSchedule(xmlfile, job.template)
        jobNew.date = job.date
        jobNew.schedule = job.schedule
        jobNew.save()
        self.parse_job(job.uid)
        self.parse_job(jobNew.uid)
        return jobNew

    def generateXmlFile(self, jobT, filename, reserve=False):
        jg = JobGen()
        xml = jg.getXML(jobT, reserve)
        tmp_path = None
        if filename.startswith('/'):
            tmp_path = filename
        else:
            tmp_path = "%s/xmls/%s" % (settings.STORAGE_ROOT, filename)
            tmp_path = re.sub(r'//+', '/', tmp_path)
            tmp_dir = os.path.dirname(tmp_path)
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
        with open(tmp_path, "w") as fd:
            fd.write(xml)
        return tmp_path

    def return2beaker(self, recipe):
        if not isinstance(recipe, Recipe):
            msg = "This type is not supported: %s %s" % (recipe, type(recipe))
            raise TypeError(msg)
        if not recipe.is_running():
            logger.info("The recipe (%s) is not already running" % recipe.uid)
            return True
        # if system status is reserved
        try:
            # from returns import return_reservation
            # status = return_reservation(int(recipe.uid))
            status = self.systemRelease(recipe)
            self.parse_job(recipe.job.uid)
            return (status == -1)
        except ImportError:
            logger.warning("No module named bkr.client")

    def systemRelease(self, recipe):
        if not isinstance(recipe, Recipe):
            msg = "This type is not supported: %s %s" % (recipe, type(recipe))
            raise TypeError(msg)
        return self.execute("system-release", recipe.system.hostname)

    def scheduleFromContent(self, xmlcontent):
        logger.error("Method is not implemented")

    def scheduleFromXmlFile(self, xmlfile):
        if not os.path.isfile(xmlfile):
            logger.error("XML file '%s' doesn't exist." % xmlfile)
            return None
        result = self.execute("job-submit", xmlfile)
        return re.findall(r"'(J:[0-9]+)'", result[0])

    def __jobSchedule(self, xmlfile, jobT):
        jobids = self.scheduleFromXmlFile(xmlfile)
        if len(jobids) > 0:
            job, st = Job.objects.get_or_create(uid=jobids[0], template=jobT,
                                                defaults={"is_finished": False, })
            return job
        logger.error("Problem with scheduling of the jobs from template (%s)."
                     % jobT.id)
        return None

    def _getXMLRPCClient(self):
        client = xmlrpclib.Server(self.server_url, verbose=0)
        if self.server_url.startswith("https"):
            # workaround ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
            # certificate verify failed (_ssl.c:590)
            if sys.version_info >= (2, 7, 9):
                client = xmlrpclib.Server(self.server_url, verbose=0,
                                          context=ssl._create_unverified_context())

        if self.username and self.password:
            client.auth.login_password(self.username, self.password)
        return client

    def parse_job(self, jobid, running=True, date_created=None):
        client = self._getXMLRPCClient()
        data = client.taskactions.task_info(jobid)

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
        if date_created:
            defaults["date"] = date_created
        job, status = Job.objects.get_or_create(uid=jobid, defaults=defaults)
        job.template = jt
        job.is_running = not data["is_finished"]

        if ((running and job.is_running) or not job.is_finished):
            content = client.taskactions.to_xml(jobid)
            dom = xml.dom.minidom.parseString(content)

            for recipexml in dom.getElementsByTagName("recipe"):
                parse_recipe(recipexml, job)

        if not job.is_running:
            job.is_finished = True
        job.save()

    def listLogs(self, recipe):
        #       doesn't work, call shell command:
        #       client = self._getXMLRPCClient()
        #       return client.recipes.files(int(recipe))
        raw, status = self.execute("job-logs", recipe)
        return raw.split()

    def downloadLog(self, logurl):
        """ Download and save beaker's log file to default storage """
        logparse = urlparse(logurl)
        logpath = os.path.join(
            settings.STORAGE_ROOT, *(logparse.path.split("/")))
        logdir = os.path.dirname(logpath)
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        try:
            rawfile = urllib2.urlopen(logurl)
        except urllib2.HTTPError as e:
            logger.warning("urllib2: http %d: %s" % (e.code, logurl))
            return
        logger.debug("download logfile: %s" % logurl)
        of = open(logpath, 'wb')
        of.write(rawfile.read())
        of.close()
        return logparse.path

    def listJobs(self, filter={}):
        """List and filter beaker jobs."""
        client = self._getXMLRPCClient()
        return client.jobs.filter(filter)


class JobGen:

    def getXML(self, jobT, reserve=False, **kwargs):
        recipesT = RecipeTemplate.objects\
            .filter(jobtemplate=jobT, is_virtualguest=False)
        # .select_related("distro", "virtualguests")
        recipesS = list()
        for recipeT in recipesT:
            if len(recipeT.getArchsForToday()) == 0:
                raise Exception("JobTemplate %d: arch is not set" % jobT.id)

            recipeT.cache_tasks = self.__generateRecipe(recipeT, jobT, reserve)
            recipeT.cache_guests = list()
            recipesS.append(recipeT)

            recipeT.cache_reserve = recipeT.is_reserve()
            if reserve:
                recipeT.cache_reserve = True

            for gRecipeT in recipeT.virtualguests.all():
                gRecipeT.cache_tasks = self.__generateRecipe(gRecipeT, jobT,
                                                             reserve)
                recipeT.cache_guests.append(gRecipeT)

        # if schedule plan doesn't exist then used all of archs to schedule
        if len(recipesS) == 0:
            raise Exception("JobTemplate %d: recipesS is 0" % jobT.id)

        jobT.cache_recipes = recipesS
        kwargs['job'] = jobT
        kwargs['default_packages'] = settings.BEAKER_DEFAULT_PACKAGES
        kwargs['reservesys'] = settings.BEAKER_RESERVESYS
        content = self.__renderXML(kwargs)
        return content

    def __renderXML(self, kwargs):
        path = os.path.dirname(__file__)
        with open("%s/%s" % (path, "beaker.xml")) as fd:
            return re.sub(r'((?<=\>)|^)\s*((?=\<)|$)', '',
                          Template(fd.read()).render(Context(kwargs)))

    def __generateRecipe(self, recipeT, jobT, reserve):
        cache_tasks = list()
        params = {}

        # at first show tasks which have be before groups
        # TaskTemplate.PRE_GROUP and TaskTemplate.BEGIN
        tasksT = TaskTemplate.objects.filter(recipe=recipeT)\
            .filter(position__in=(TaskTemplate.PRE_GROUP, TaskTemplate.BEGIN))\
            .select_related("test").order_by("priority").distinct()
        for taskT in tasksT:
            if not taskT.test.is_enable:
                continue
            cache_tasks.append(self.__generateTask(taskT))

        # show task from groups of task
        for taskG in recipeT.grouptemplates.order_by("priority"):
            params = taskG.get_params()
            for taskT in taskG.group.grouptests.order_by("priority"):
                if not taskT.test.is_enable:
                    continue
                params2 = taskT.get_params()
                params2.update(params)
                taskT.parent_params = params2
                cache_tasks.append(self.__generateTask(taskT))

        # other tasks show after groups
        # TaskTemplate.POST_GROUP and TaskTemplate.END
        tasksT = TaskTemplate.objects.filter(recipe=recipeT)\
            .filter(position__in=(TaskTemplate.POST_GROUP, TaskTemplate.END))\
            .select_related("test").order_by("priority").distinct()
        for taskT in tasksT:
            if not taskT.test.is_enable:
                continue
            cache_tasks.append(self.__generateTask(taskT))
        return cache_tasks

    def __generateTask(self, taskT):
        params = taskT.get_params()
        hasattr(taskT, "parent_params") and params.update(taskT.parent_params)
        return {"name": taskT.test.name,
                "params": params,
                "priority": taskT.priority,
                "role": taskT.role,
                "get_role": taskT.get_role,
                }


def parse_task(taskxml, recipe):
    testname = taskxml.getAttribute("name")
    test, status = Test.objects.get_or_create(name=testname, defaults={
        "owner": Author.parseAuthor("")
    })

    uid = taskxml.getAttribute("id")
    status_str = taskxml.getAttribute("status")
    result = taskxml.getAttribute("result")
    task_alias = None
    for params in taskxml.getElementsByTagName("params"):
        for param in params.getElementsByTagName("param"):
            if param.getAttribute("name") == "TASK_ALIAS":
                task_alias = param.getAttribute("value")

    task, status = Task.objects.get_or_create(
        uid=uid,
        defaults={
            "recipe": recipe,
            "test": test,
            "alias": task_alias,
        }
    )
    task.set_result(result)
    task.set_status(status_str)

    if task.is_completed():
        task.duration = float(strToSec(taskxml.getAttribute("duration")))
    task.save()


def parse_recipe(recipexml, job, guestrecipe=None):
    uid = recipexml.getAttribute("id")
    hostname = recipexml.getAttribute("system")
    str_arch = recipexml.getAttribute("arch")
    str_distro = recipexml.getAttribute("distro")
    whiteboard = recipexml.getAttribute("whiteboard")
    str_status = recipexml.getAttribute("status")
    str_result = recipexml.getAttribute("result")

    system, status = System.objects.get_or_create(
        hostname=hostname,
    )

    arch, status = Arch.objects.get_or_create(
        name=str_arch,
    )

    distro, status = Distro.objects.get_or_create(
        name=str_distro,
    )

    recipe, status = Recipe.objects.get_or_create(
        uid=uid,
        defaults={
            "job": job,
            "system": system,
            "whiteboard": whiteboard,
            "distro": distro,
            "arch": arch}
    )
    recipe.system = system
    recipe.set_result(str_result)

    recipe.set_status(str_status)
    if status:
        recipe.save()

    for dataxml in recipexml.childNodes:
        if dataxml.tagName == "guestrecipe" and not guestrecipe:
            parse_recipe(dataxml, job, recipe)
        if dataxml.tagName == "task":
            parse_task(dataxml, recipe)

    recipe.recount_result()
    recipe.save()

    reserve = Task.objects.filter(
        test__name=settings.RESERVE_TEST, recipe=recipe)

    logger.debug("%s status:  %s result %s" %
                 (recipe.uid, recipe.status, recipe.result))
    if reserve or recipe.status == Recipe.RESERVED:
        if recipe.result == PASS and job.template.event_finish == RETURNWHENGREEN:
            bk = Beaker()
            bk.return2beaker(recipe)
            bk.systemRelease(recipe)

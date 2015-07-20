#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 20.07.2014

import xmlrpclib
import os
import sys
import re
import urllib2
import xml.dom.minidom
import time
import logging
import pxssh
import subprocess
from datetime import datetime, timedelta
from django.conf import settings
from django.template.defaultfilters import slugify
from django.template import Context, Template
from apps.core.models import JobTemplate, RecipeTemplate, TaskTemplate
from apps.core.models import Job, Recipe, Test, Task
from apps.core.models import System, Arch, Distro, Author, PASS, RETURNWHENGREEN


logger = logging.getLogger(__name__)


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

    def execute(self, command, param):
        """
            Execute beaker command
        """
        auth = ""
        if settings.BEAKER_OWNER:
            auth = " --username=%s --password=%s" % (settings.BEAKER_OWNER,
                                                     settings.BEAKER_PASS)
        command = "bkr %s %s%s" % (command, param, auth)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return p.communicate()

    def jobCancel(self, job, message=""):
        if not isinstance(job, Job) or not job:
            raise Exception("Parameter 'job' is not instance of class Job")
        result = self.execute("job-cancel", "--msg \"%s\" %s" % (message,
                                                                 job.uid))
        if re.search("Cancelled\s+%s" % job.uid, result[0]):
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
        tmp = "__tmp__"
        path = "%s/%s.xml" % (date, tmp)
        xmlfile, job = None, None
        try:
            xmlfile = self.generateXmlFile(jobT, path, reserve)
            job = self.__jobSchedule(xmlfile, jobT)
        except:
            # FIXME
            # TypeError: argument 1 must be string or read-only character
            # buffer, not None
            logging.error("schedule file %s: %s %s" % (xmlfile, job, jobT))
        if job:
            os.rename(xmlfile, xmlfile.replace(tmp, slugify(job.uid)))
        return job

    def jobReschedule(self, job, message):
        self.jobCancel(job, message)
        date = job.date.date().isoformat()
        path = "%s/%s.reschedule.xml" % (date, slugify(job.id))
        # A potential problem with reservesys
        xmlfile = self.generateXmlFile(job.template, path)
        jobNew = self.__jobSchedule(xmlfile, job.template)
        jobNew.date = job.date
        jobNew.save()
        return jobNew

    def generateXmlFile(self, jobT, filename, reserve=False):
        jg = JobGen()
        xml = jg.getXML(jobT, reserve)
        tmp_path = None
        if filename.startswith('/'):
            tmp_path = filename
        else:
            tmp_path = "%s/data/xmls/%s" % (settings.ROOT_PATH, filename)
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
            from returns import return_reservation
            status = return_reservation(int(recipe.uid))
            import sdsdssdsd
            return (status == -1)
        except ImportError:
            logger.info("No module named bkr.client")

    def return2beaker_old(self, recipe):
        # better way: use fabric
        ssh = pxssh.pxssh()
        ssh.force_password = True
        result = False
        try:
            ssh.login(hostname, settings.BKR_SYSTEM_USER,
                      settings.BKR_SYSTEM_PASS)
            ssh.sendline('uptime')
            ssh.prompt(timeout=20)
            bash_comm = ("[ -e ~/reserved.lock ] || "
                         "(return2beaker.sh 2> /dev/null && echo 'YAHOO' || "
                         "echo 'NO')")
            # bash_comm = ("[ -e ~/reserved.lock ] || return2beaker.sh || "
            #    " (rhts-abort -t recipe -l $(grep RESULT_SERVER /etc/motd |"
            #    " cut -d'=' -f2) -r $(cat /root/RECIPE.TXT) && halt)")
            ssh.sendline(bash_comm)
            ssh.prompt(timeout=20)
            if ssh.before.find("YAHOO") == -1:
                result = self.jobCancel(recipe.job, "Emergency solution of "
                                        "return2beaker")
        except Exception:
            logger.exception("Problem with return2beaker of the recipe (%s|%s)"
                             % (recipe.uid, recipe.job.uid))
            result = self.jobCancel(recipe.job, "Emergency solution of "
                                    "return2beaker")
        finally:
            try:
                ssh.logout()
            except:
                pass
        return result

    def scheduleFromXmlFile(self, xmlfile):
        if not os.path.isfile(xmlfile):
            logger.error("XML file '%s' does not exist." % xmlfile)
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
        return self.__renderXML(kwargs)

    def __renderXML(self, kwargs):
        path = os.path.dirname(__file__)
        with open("%s/%s" % (path, "beaker.xml")) as fd:
            return re.sub(r'((?<=\>)|^)\s*((?=\<)|$)', '',
                          Template(fd.read()).render(Context(kwargs)))

    def __generateRecipe(self, recipeT, jobT, reserve):
        cache_tasks = list()
        params = {}
        for taskG in recipeT.grouptemplates.order_by("priority"):
            params = taskG.get_params()
            for taskT in taskG.group.grouptests.order_by("priority"):
                if not taskT.test.is_enable:
                    continue
                params2 = taskT.get_params()
                params2.update(params)
                taskT.parent_params = params2
                cache_tasks.append(self.__generateTask(taskT))

        tasksT = TaskTemplate.objects.filter(recipe=recipeT)\
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

#   stat = dict()
#    for result in taskxml.childNodes:
#        for it in result.childNodes:
# print it.getAttribute("id"), it.getAttribute("result")
#            res = it.getAttribute("result")
#            if not res: continue
#            if stat.has_key(res):
#                stat[res] += 1
#            else:
#                stat[res] = 1

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

    # Download data from journal.xml
    # task_full_xml = None
    # response = None
    # try:
    #  response = urllib2.urlopen(settings.BEAKER_TASK_LOG+"%s+/%s/journal.xml")
    #  task_full_xml = parse(response)
    # except:
    #  pass
    # finally:
    #  if response:
    #    response.close()
    #
    # if task_full_xml:
    #   task_full_xml.getElementsByTagName('starttime')[0].childNodes[0].nodeValue.strip()

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

    # journal = otask.load_journal()
    # if journal:
    #    print "journal: ", journal
    #    print parseJournals(journal)

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


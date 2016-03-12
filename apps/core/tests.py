"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import difflib
import glob
import os

from bs4 import BeautifulSoup
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

import apps.core.views.tests
from apps.core.models import Job, RecipeTemplate, TestHistory
from apps.core.utils.beaker import Beaker, JobGen
from apps.core.utils.beaker_import import Parser
from apps.taskomatic.models import TaskPeriodSchedule


def get_content_from_file(filename):
    f = open(filename)
    xml_content = f.read()
    f.close()
    return xml_content


class ImportTest(TestCase):

    def xmlimport(self, filename, num_recipes=1):
        """
        Tests importing beaker xml and crete templates
        """
        s = Parser(file=filename)
        s.run(position=100)

        recipes = RecipeTemplate.objects.filter(jobtemplate=s.job)

        self.assertEqual(
            len(recipes), num_recipes, msg="Number recipes is bad")
        self.assertEqual(s.job.position, 100, msg="job position is same")

        # workaround: ignore default packages
        settings.BEAKER_DEFAULT_PACKAGES = []

        job = JobGen()
        xml = job.getXML(s.job)
        xml_old = get_content_from_file(filename)

        xml = u"%s" % "".join(xml.splitlines(True))
        xml_old = u"%s" % "".join(xml_old.splitlines(True))

        bs1 = BeautifulSoup(xml_old, "lxml")
        bs2 = BeautifulSoup("".join(xml), "lxml")

        d = difflib.unified_diff(
            bs1.prettify().split("\n"),
            bs2.prettify().split("\n"))
        diff = "\n".join(d)

        print "-----------"
        print "'%s'" % diff
        print "-----------"

        self.assertEqual(len(diff), 0, msg="XML '%s' is different" % filename)

#    def test_virtquest_import(self):
#        self.xmlimport("test/example.2.xml", num_recipes=2)

    def test_basic_import(self):
        pwd = os.path.dirname(__file__)
        for xmltestfile in glob.glob(
                "%s/example.*" % os.path.join(pwd, "tests")):
            self.xmlimport(xmltestfile)


class SimpleTest(TestCase):

    # anonymous users
    def test_running_anonym(self):
        pages = ["/", "/diffs.html", "/jobs.html", "/tests.html", "/admin/login/", "/reports/"]

        c = Client()
        for url in pages:
            r = c.get(url)
            self.assertEqual(r.status_code, 200, msg="page %s is not running" % url)

    # login user
    def test_running_auth(self):
        username, password = "user1", "pass1"
        c = Client()
        user = User.objects.create_user(username, 'user1@localhost', password)
        self.assertIsNotNone(user)
        pages = ["/admin/", ]

        c.login(username=username, password=password)
        for url in pages:
            r = c.get(url, follow=True)
            self.assertEqual(r.status_code, 200, msg="page %s is not running (%s)" % (url, r.status_code))


class BeakerTest(TestCase):

    def test_create_job(self):
        bkr = Beaker()

        pwd = os.path.dirname(__file__)
        xmlpath = os.path.join(pwd, "tests", "example.fedora.xml")

        # xmlcontent = get_content_from_file(xmlpath)
        # self.assertIsNotNone(xmlcontent, msg="file %s is not load" % xmlcontent)
        jobids = bkr.scheduleFromXmlFile(xmlpath)

        for jobid in jobids:
            self.assertIsNotNone(jobid, msg="job is not created")

            # check jobs from beaker
            bkr.parse_job(jobid)

            job = Job.objects.get(uid=jobid)

            # cancel created job
            bkr.jobCancel(job)


class TestsGetHistory(TestCase):
    fixtures = ['apps/core/tests/db-TestsGetHistory.json']

    def test_get_history(self):
        period_schedule_ids = [4, 5]   # IDs required period schedules have in DB
        exp_period_ids = [11, 12]   # Counts required period schedule IDs should have
        exp_changes_ids = [3, 4, 6]   # These changes should be relevant for given period_schedule_ids
        exp_changes = TestHistory.objects.filter(id__in=exp_changes_ids).order_by('id')
        self.assertEqual(3, len(exp_changes))
        exp_test_id = 5
        expected = {
            exp_test_id: {
                exp_period_ids[0]: [exp_changes[0]],
                exp_period_ids[1]: [exp_changes[1], exp_changes[2]]
            }
        }
        out = apps.core.views.tests.get_history(period_schedule_ids)
        self.assertItemsEqual(expected, out)

    def test_get_matching_period_for_change(self):
        changes = TestHistory.objects.all().order_by('id')
        periods = TaskPeriodSchedule.objects.filter(counter__in=[12, 13])
        # Far before range
        periods = TaskPeriodSchedule.objects.filter(counter__in=[12, 13])
        with self.assertRaises(Exception):
            out = apps.core.views.tests.get_matching_period_for_change(periods, changes[0])
        # Just before range (first part of range is somewhat special, see
        # docs string on the function in test)
        periods = TaskPeriodSchedule.objects.filter(counter__in=[10, 11, 12])
        out = apps.core.views.tests.get_matching_period_for_change(periods, changes[2])
        self.assertEqual(periods.order_by('counter')[1], out)
        # In range
        periods = TaskPeriodSchedule.objects.filter(counter__in=[10, 11, 12])
        out = apps.core.views.tests.get_matching_period_for_change(periods, changes[3])
        self.assertEqual(periods.order_by('counter')[2], out)
        # After range
        periods = TaskPeriodSchedule.objects.filter(counter__in=[10, 11, 12])
        with self.assertRaises(Exception):
            out = apps.core.views.tests.get_matching_period_for_change(periods, changes[4])

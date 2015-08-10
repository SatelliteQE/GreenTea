"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import difflib
import glob
import os

from django.test import TestCase
from django.test.client import Client

from apps.core.models import RecipeTemplate
from apps.core.utils.beaker import Beaker, JobGen
from apps.core.utils.beaker_import import Parser


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

        job = JobGen()
        xml = job.getXML(s.job)
        xml_old = get_content_from_file(filename)
        xml = xml.splitlines(True)
        xml_old = xml_old.splitlines(True)
        d = difflib.unified_diff(xml, xml_old)
        diff = "".join(d)

        print "-----------"
        print "'%s'" % diff
        print "-----------"

        self.assertEqual(len(diff), 0, msg="XML '%s' is different" % filename)

#    def test_virtquest_import(self):
#        self.xmlimport("test/example.2.xml", num_recipes=2)

    def test_basic_import(self):
        pwd = os.path.dirname(__file__)
        for xmltestfile in glob.glob("%s/example.*" % os.path.join(pwd, "tests")):
            self.xmlimport(xmltestfile)


class SimpleTest(TestCase):

    def test_running(self):

        c = Client()
        r = c.get("/")
        self.assertEqual(r.status_code, 200, msg="homepage is not running")

        r = c.get("/jobs.html")
        self.assertEqual(r.status_code, 200, msg="jobs page is not running")

        r = c.get("/tests.html")
        self.assertEqual(r.status_code, 200, msg="tests page is not running")


class BeakerTest(TestCase):

    def test_create_job(self):
        bkr = Beaker()

        pwd = os.path.dirname(__file__)
        xmlpath = os.path.join(pwd, "tests", "example.fedora.xml")

        #xmlcontent = get_content_from_file(xmlpath)
        #self.assertIsNotNone(xmlcontent, msg="file %s is not load" % xmlcontent)

        #jobid = bkr.scheduleFromXmlFile(xmlpath)
        jobid = ("J:1045253", )
        self.assertIsNotNone(jobid, msg="job is not created")

        print bkr.parse_job(jobid)

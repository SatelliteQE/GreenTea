"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from apps.core.utils.beaker_import import Parser
from apps.core.models import RecipeTemplate
from apps.core.utils.job_generator import JobGen, render_job
import difflib

class ImportTest(TestCase):
    def xmlimport(self, filename, num_recipes=1):
        """
        Tests importing beaker xml and crete templates
        """
        s = Parser(file=filename) 
        s.run(position=100)

        recipes = RecipeTemplate.objects.filter(jobtemplate=s.job)

        self.assertEqual(len(recipes), num_recipes, msg="Number recipes is bad")
        self.assertEqual(s.job.position, 100, msg="job position is same")

        job = JobGen(job=s.job, reserve=False)
        xml = render_job(job, is_manual=True)
        f = open(filename)
        xml_old = f.read()
        f.close()
        xml=xml.splitlines(True)
        xml_old=xml_old.splitlines(True)
        d = difflib.unified_diff(xml, xml_old)
        diff = "".join(d)

        print "-----------"
        print "'%s'" % diff
        print "-----------"

        self.assertEqual(len(diff), 0, msg="XML '%s' is different" % filename )

#    def test_virtquest_import(self):
#        self.xmlimport("test/example.2.xml", num_recipes=2)

    def test_basic_import(self):
        self.xmlimport("test/example.1.xml")


class SimpleTest(TestCase):
    def test_running(self):

        c = Client()
        r = c.get("/")
        self.assertEqual(r.status_code, 200, msg="homepage is not running")

        r = c.get("/jobs.html")
        self.assertEqual(r.status_code, 200, msg="jobs page is not running")

        r = c.get("/tests.html")
        self.assertEqual(r.status_code, 200, msg="tests page is not running")


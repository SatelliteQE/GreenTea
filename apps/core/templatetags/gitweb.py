import re

from django import template
from django.conf import settings

from apps.core.models import Test, TestHistory

register = template.Library()


@register.filter
def getUrlToGit(test):
    if isinstance(test, Test) and test.git and test.git.name:
        res = re.match(r'.*/([^/]+)$', test.git.name)
        if res:
            gName = res.group(1)
            tName = re.sub(r'.*%s' % gName, '', test.name)
            return "%s%s/.git/tree/HEAD:%s" % (settings.GITWEB_URL, gName,
                                               tName)
    return settings.GITWEB_URL


@register.filter
def getUrlToCommit(testHistory):
    print testHistory.test
    if isinstance(testHistory, TestHistory) and\
       isinstance(testHistory.test, Test) and testHistory.test.git and\
       testHistory.test.git.name:
        res = re.match(r'.*/([^/]+)$', testHistory.test.git.name)
        if res:
            gName = res.group(1)
            return "%s%s/.git/commit/%s" % (settings.GITWEB_URL, gName,
                                            testHistory.commit)
    return settings.GITWEB_URL

import datetime
import os
import posixpath
import re
import stat
import urllib

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def nostartsdate(value):
    labeldates = re.findall(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})", value)
    if labeldates:
        return value[11:]
    return value


@register.filter
def keyvalue(dict, key):
    if not dict:
        return None
    return dict.get(key)


@register.filter
def itemvalue(list, ix):
    if ix < 0 or ix >= len(list):
        return None
    return list[ix]


@register.filter
def percent(data, val):
    return val * 100. / data


@register.filter
def sum(data, key):
    return data["sum"][key]


@register.filter
def diffsec(date1, date2):
    """ Return number of secondes between two datetimes, positive number is past, negativ number is future. """
    def convert(dd):
        if isinstance(dd, datetime.date):
            return datetime.datetime(dd.year, dd.month, dd.day)
        return dd
    return (convert(date1) - convert(date2)).total_seconds()


@register.filter()
def htmlentities(s):
    return mark_safe(escape(s).encode('ascii', 'xmlcharrefreplace'))


@register.simple_tag
def staticfile(path):
    normalized_path = posixpath.normpath(urllib.unquote(path)).lstrip('/')
    absolute_path = os.path.join(settings.ROOT_PATH, 'tttt', normalized_path)
    if absolute_path:
        return '%s?v=%s' % (path, os.stat(absolute_path)[stat.ST_MTIME])
    return path

#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 2013-2015

from django.db import models

from apps.core.models import Job, Recipe, Task, Test
from django.utils import timezone

class Comment(models.Model):
    ENUM_ACTION_NONE = 0
    ENUM_ACTION_WAIVED = 1
    ENUM_ACTION_RETURN = 2
    ENUM_ACTION_RESCHEDULE = 3
    ENUM_ACTION = (
        (ENUM_ACTION_NONE, "just comment"),
        (ENUM_ACTION_WAIVED, "mark waived"),
        (ENUM_ACTION_RETURN, "return2beaker"),
        (ENUM_ACTION_RESCHEDULE, "reshedule job"),
    )
    job = models.ForeignKey(Job, blank=True, null=True)
    recipe = models.ForeignKey(Recipe, blank=True, null=True,
                               related_name='comments')
    task = models.ForeignKey(Task, blank=True, null=True,
                             related_name='comments')
    test = models.ForeignKey(Test, blank=True, null=True)
    username = models.CharField(max_length=32)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    action = models.SmallIntegerField(
        choices=ENUM_ACTION, default=ENUM_ACTION_NONE)

    def __unicode__(self):
        return "%s %s" % (self.username, self.created_date)

    def get_action(self):
        return dict(self.ENUM_ACTION)[self.action]

    def set_time(self, tdate=None):
        if not tdate:
            tdate = timezone.now()
        self.created_date = tdate
        self.save()

    def is_waived(self):
        return (self.action == self.ENUM_ACTION_WAIVED)

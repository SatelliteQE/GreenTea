from django.db import models
from apps.core.models import Job, Recipe, Task
from datetime import datetime
from apps.core.utils.date_helpers import currentDate2, TZDateTimeField
import json
from south.modelsinspector import add_introspection_rules
add_introspection_rules(
    [], ["^apps\.core\.utils\.date_helpers\.TZDateTimeField"])


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
    recipe = models.ForeignKey(Recipe, blank=True, null=True)
    task = models.ForeignKey(Task, blank=True, null=True)
    username = models.CharField(max_length=32)
    content = models.TextField()
    #created_date = TZDateTimeField(default=currentDate())
    created_date = models.DateTimeField(default=currentDate2())
    action = models.SmallIntegerField(
        choices=ENUM_ACTION, default=ENUM_ACTION_NONE)

    def __unicode__(self):
        return "%s %s" % (self.username, self.created_date)

    def get_action(self):
        return dict(self.ENUM_ACTION)[self.action]

    def set_time(self):
        self.created_date = currentDate2()
        self.save()

    def to_json(self):
        return {
            #'job': self.job.to_json() if self.job else None,
            'username': self.username,
            'content': self.content,
            'created_date': self.created_date.strftime("%Y-%m-%d %H:%M:%S"),
            'action': self.get_action_display()
        }

    def is_waived(self):
        return (self.action == self.ENUM_ACTION_WAIVED)

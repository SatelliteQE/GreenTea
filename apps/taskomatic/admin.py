from django.contrib import admin

from models import *


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'common', 'date_run', 'get_time_long')


class TaskPeriodAdmin(admin.ModelAdmin):
    list_display = ("title", "common", "cron", "get_previous_run", "is_enable")


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskPeriodSchedule)
admin.site.register(TaskPeriod, TaskPeriodAdmin)

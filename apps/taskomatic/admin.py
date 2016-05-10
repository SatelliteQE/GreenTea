import logging
from django.contrib import admin

from models import Task, TaskPeriod, TaskPeriodSchedule
from apps.report.models import Score

logger = logging.getLogger("main")


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'common', 'date_run', 'get_time_long')


class TaskPeriodAdmin(admin.ModelAdmin):
    list_display = ("title", "common", "cron", "get_previous_run", "is_enable")

    def recount(modeladmin, request, queryset):
        for it in queryset:
            it.recount_all()
    recount.short_description = "Recount periods"
    actions = [recount, ]


class TaskPeriodScheduleAdmin(admin.ModelAdmin):
    list_display = ("title", "period", "counter", "date_create")
    search_fields = ("title", "id")
    list_filter = ("period", )

    def recount_score(modeladmin, request, queryset):
        for it in queryset:
            a, b = Score.recount_by_schedule(it)
        logger.info("Run %d recounts score %d tests (from %d tasks)" % (it.id, a, b))
    recount_score.short_description = "Recount score for selected runs"
    actions = [recount_score]


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskPeriodSchedule, TaskPeriodScheduleAdmin)
admin.site.register(TaskPeriod, TaskPeriodAdmin)

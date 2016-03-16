from django.contrib import admin

from models import Task, TaskPeriod, TaskPeriodSchedule


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'common', 'date_run', 'get_time_long')


class TaskPeriodAdmin(admin.ModelAdmin):
    list_display = ("title", "common", "cron", "get_previous_run", "is_enable")

    def recount(modeladmin, request, queryset):
        for it in queryset:
            it.recount_all()
    recount.short_description = "Recount periods"
    actions = [recount,]


class TaskPeriodScheduleAdmin(admin.ModelAdmin):
    list_display = ("title", "period", "counter", "date_create")
    search_fields = ("title", "id")
    list_filter = ("period", )


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskPeriodSchedule, TaskPeriodScheduleAdmin)
admin.site.register(TaskPeriod, TaskPeriodAdmin)

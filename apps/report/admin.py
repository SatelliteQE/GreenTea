from django.contrib import admin
from models import Report


class ReportAdmin(admin.ModelAdmin):
    filter_horizontal = ('jobs',)

admin.site.register(Report, ReportAdmin)

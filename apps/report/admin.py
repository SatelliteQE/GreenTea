#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik <pstudeni@redhat.com>
# Year: 2016

from django.contrib import admin

from models import ExternalPage, Report, Score


class ReportAdmin(admin.ModelAdmin):
    filter_horizontal = ('jobs',)


class ScoreAdmin(admin.ModelAdmin):
    list_display = ["test", "score", "rate", "schedule"]
    search_fields = ["test__name"]


admin.site.register(Report, ReportAdmin)
admin.site.register(ExternalPage)
admin.site.register(Score, ScoreAdmin)

#!/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik <pstudeni@redhat.com>
# Year: 2016

from django.contrib import admin

from models import Report


class ReportAdmin(admin.ModelAdmin):
    filter_horizontal = ('jobs',)

admin.site.register(Report, ReportAdmin)

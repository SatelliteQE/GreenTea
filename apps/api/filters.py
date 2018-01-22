#!/bin/python
# -*- coding: utf-8 -*-

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 4.4.2016

from django_filters import Filter, FilterSet, NumberFilter

from apps.core.models import Task


class ListFilter(Filter):

    def filter(self, qs, value):
        if not value:
            return qs
        self.lookup_type = 'in'
        values = value.split(',')
        return super(ListFilter, self).filter(qs, values)


class TaskFilter(FilterSet):
    # FIXME skip filter by results
    # results = ListFilter(name='result')
    recipe = NumberFilter(name='recipe__id')

    class Meta:
        model = Task
        fields = ['recipe', 'recipe__uid', 'test', 'result',
                  'status', 'statusbyuser', 'uid']

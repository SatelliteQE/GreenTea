#!/bin/python
# -*- coding: utf-8 -*-

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 4.4.2016

from django_filters import Filter, FilterSet, NumberFilter

from apps.core.models import Task
from django_filters.fields import Lookup


class ListFilter(Filter):

    def filter(self, qs, value):
        if not value:
            return qs
        value_list = [int(x) for x in value.split(',')]
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


class TaskFilter(FilterSet):
    results = ListFilter(name='result')
    recipe = NumberFilter(name='recipe__id')

    class Meta:
        model = Task
        fields = ['recipe', 'recipe__uid', 'test', 'result',
                  'status', 'statusbyuser', 'uid']

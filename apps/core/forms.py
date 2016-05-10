# Author: Pavel Studenik <pstudeni@redhat.com>
# Date: 24.9.2013

import difflib
import logging

from django import forms

import apps.core.views
from models import GroupTemplate, GroupTestTemplate, JobTemplate, Test

logger = logging.getLogger("main")


class HomepageForm(forms.Form):
    ORDER_CHOICES = (
        ("rate", "rate"),
        ("score", "score")
    )
    order = forms.ChoiceField(
        choices=ORDER_CHOICES,
        required=False
    )
    schedule = forms.IntegerField(
        required=False
    )
    page = forms.IntegerField(
        required=False
    )

    def get_params(self):
        return "&amp;".join(["%s=%s" % (x, y) for x, y in self.cleaned_data.items()])


class FilterForm(forms.Form):
    onlyfail = forms.BooleanField(
        required=False, initial=False
    )
    search = forms.CharField(
        required=False
    )
    tag = forms.CharField(
        required=False
    )
    slider = forms.CharField(
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['search'].widget.attrs['class'] = 'form-control'
        self.fields['search'].widget.attrs['placeholder'] = 'Search'

    def clean_search(self):
        value = self.cleaned_data["search"].strip()
        return value


class GroupsForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=GroupTemplate.objects.filter().order_by("name"), empty_label=None)
    content = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': "30", 'cols': "100"}))

    def save(self):
        group = self.cleaned_data["group"]
        tasks = group.grouptests.all().order_by("priority")
        tests_exists = [it.test.name for it in tasks]

        rows = self.cleaned_data["content"]
        priority = len(tests_exists) + 1
        for testname in rows.split():
            try:
                test = Test.objects.get(name=testname.strip())
                if test.name not in tests_exists:
                    gtt = GroupTestTemplate(
                        test=test, group=group, priority=priority)
                    gtt.save()
                    priority += 1

            except Test.DoesNotExist:
                logger.warning("test %s does not exist" % testname)
        return group


class JobForm(forms.Form):
    jobs1 = forms.ModelChoiceField(queryset=JobTemplate.objects.filter(
        is_enable=True).order_by("whiteboard"), empty_label=None)
    jobs2 = forms.ModelChoiceField(queryset=JobTemplate.objects.filter(
        is_enable=True).order_by("whiteboard"), empty_label=None)

    def compare(self):
        d = difflib.HtmlDiff(wrapcolumn=90)
        job1_xml = apps.core.views.get_xml(
            self.cleaned_data["jobs1"]).splitlines(1)
        job2_xml = apps.core.views.get_xml(
            self.cleaned_data["jobs2"]).splitlines(1)
        return d.make_table(job1_xml, job2_xml)

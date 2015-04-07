from django import forms
import logging
from models import JobTemplate, GroupTemplate, Test, GroupTestTemplate

logger = logging.getLogger(__name__)


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
        def CompareRecipes(r1, r2):

            task1 = [it.test for it in r1.tasks.order_by("id")]
            task2 = [it.test for it in r2.tasks.order_by("id")]

            data = {r1: [], r2: []}

            for it in task1:
                data[r1].append((it in task2, it))

            for it in task2:
                data[r2].append((it in task1, it))

            return data

        compares = []
        for it1 in self.cleaned_data["jobs1"].trecipes.all():
            for it2 in self.cleaned_data["jobs2"].trecipes.all():
                compares.append(CompareRecipes(it1, it2))
        return compares

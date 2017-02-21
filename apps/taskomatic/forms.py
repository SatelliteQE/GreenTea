from models import TaskPeriod
from django import forms
import shlex


class TaskPeriodForm(forms.ModelForm):

    class Meta:
        model = TaskPeriod
        exclude = []

    def clean(self):
        cleaned_data = super(TaskPeriodForm, self).clean()
        # params = shlex.split(cleaned_data["common"])

    def clean_common(self):
        params = shlex.split(self.cleaned_data["common"])
        label = self.cleaned_data["label"]
        for key, it in enumerate(params):
            if it == "--schedule-label":
                if len(params) <= key + 1:
                    raise forms.ValidationError(
                        "Lissing label for --schedule-label")
                if params[key + 1] != label:
                    raise forms.ValidationError(
                        "Label should be same for --schedule-label")
        return " ".join(params)


from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.core.models import Author, Job, Recipe, Task
from apps.taskomatic.models import Task as TaskomaticTask
from apps.waiver.models import Comment


class WaiverForm(forms.ModelForm):
    uids = forms.fields.CharField(required=True)
    action = forms.fields.CharField(required=True)

    class Meta:
        model = Comment
        fields = ('content', 'username')

    def clean_uids(self):
        uids = self.cleaned_data["uids"].split(" ")
        # print uids
        uid_list = []
        for uid in uids:
            if uid.startswith("R:"):
                uid_list.append(Recipe.objects.get(uid=uid[2:]))
            if uid.startswith("J:"):
                uid_list.append(Job.objects.get(uid=uid))
            if uid.startswith("T:"):
                uid_list.append(Task.objects.get(uid=uid[2:]))
        if not uid_list:
            raise forms.ValidationError(_(u'You must fill beaker\'s unique id '
                                          'of task, recipe or jobs'))
        return uid_list

    def clean_action(self):
        action = int(self.cleaned_data["action"])
        if action not in [Comment.ENUM_ACTION_NONE,
                          Comment.ENUM_ACTION_RETURN,
                          Comment.ENUM_ACTION_RESCHEDULE,
                          Comment.ENUM_ACTION_WAIVED]:
            raise forms.ValidationError(_(u'Wrong choice of action'))
        return action

    def clean_content(self):
        return self.cleaned_data["content"].strip()

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        author = Author.objects.filter(email__startswith=username)
        return author[0].name if len(author) > 0 else username

    def __esc(self, mes):
        return mes.replace("'", "\\'")

    def save(self):
        for it in self.cleaned_data["uids"]:
            data = {
                "content": self.__esc(self.cleaned_data.get("content",
                                                            "")),
                "username": self.cleaned_data["username"],
                "action": self.cleaned_data["action"],
            }
            data["recipe"] = it if isinstance(it, Recipe) else None
            data["job"] = it if isinstance(it, Job) else None
            if isinstance(it, Task):
                data["task"] = it
                data["recipe"] = it.recipe
            else:
                data["task"] = None
            # print data
            oComment = Comment(**data)
            oComment.save()

            # FIXME workaround: date is set by last restart application
            # we don't know why
            oComment.set_time()

            if data["action"] == Comment.ENUM_ACTION_RETURN and\
               isinstance(it, Recipe):
                task = TaskomaticTask(title="WebUI: beaker return2beaker",
                                      common="beaker")
                task.common_params = "beaker return2beaker "\
                    "--return2beaker-recipe='R:%(recipe)s' "\
                    "--reschedule-message='%(content)s'" % \
                                     data
                task.save()
            if data["action"] == Comment.ENUM_ACTION_RESCHEDULE:
                task = TaskomaticTask(title="WebUI: beaker reschedule",
                                      common="beaker")
                uid = None
                if isinstance(it, Recipe):
                    uid = data["recipe"].job.uid
                elif isinstance(it, Job):
                    uid = data["job"].uid
                task.common_params = "beaker reschedule "\
                                     "--reschedule-job='%s' "\
                                     "--reschedule-message='%s'" % \
                    (uid, self.__esc(self.cleaned_data
                                     .get("content", "")))
                task.save()
            if oComment.is_waived() and oComment.recipe and not data["task"]:
                oComment.recipe.set_waived()
            elif oComment.is_waived() and oComment.task:
                oComment.task.set_waived()

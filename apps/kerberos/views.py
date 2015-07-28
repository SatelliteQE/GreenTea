#! /usr/bin/env python
# author: Pavel Studenik <pstudeni@redhat.com>

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = 'login.html'

    def dispatch(self, *args, **kwargs):
        self.remote_user = self.request.META[
            "REMOTE_USER"] if self.request.META.has_key("REMOTE_USER") else None

        if not self.remote_user:
            return redirect(reverse("admin:index"))

        username, real = self.remote_user.split("@")
        email = self.remote_user.lower()
        password = "nimda"  # TODO better default password

        if self.remote_user != None:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(username, email, password)
                user.is_staff = True
                user.save()

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(self.request, user)

            return redirect("homepage")

        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

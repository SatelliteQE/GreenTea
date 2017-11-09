#! /usr/bin/env python
# author: Pavel Studenik <pstudeni@redhat.com>

import logging
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings

logger = logging.getLogger("main")

class LoginView(TemplateView):
    template_name = 'login.html'

    def dispatch(self, *args, **kwargs):
        self.remote_user = self.request.META[
            "REMOTE_USER"] if "REMOTE_USER" in self.request.META else None
        logger.info("Kerberos: %s" % self.remote_user)
        if not self.remote_user:
            return redirect(reverse("admin:index"))

        username, real = self.remote_user.split("@")
        email = self.remote_user.lower()
        password = settings.DEFAULT_KERBEROS_PASSWORD

        if self.remote_user is not None:
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

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

# Author: Martin Korbel
# Email: mkorbel@redhat.com
# Date: 20.07.2014

import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import Git

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # This is optional attribute, if we want to change default command name
    # for Taskomatic.
    COMMAND_NAME = "checkrepo"

    args = '[reponame ...]'
    help = ("Load/refresh data from gits.")
    requires_system_checks = True
    can_import_settings = True

    def handle(self, *args, **kwargs):
        repos = list()
        for arg in args:
            if arg.strip():
                repos.append(arg)
        for path in settings.REPOSITORIES_GIT:
            for repo in settings.REPOSITORIES_GIT[path]:
                if len(repos) > 0 and repo not in repos:
                    continue
                if not os.path.exists(os.path.join(path, repo)):
                    logger.error("repo %s doesn't exists in %s" % (repo, path))
                    continue
                git = Git.getGitFromFolder(os.path.join(path, repo))
                git.log = logger
                if git:
                    try:
                        logger.info("Checking the GIT '%s' repo" % repo)
                        git.refresh()
                        git.updateInformationsAboutTests()
                    except Exception:
                        logger.exception("Problem with git %s" % repo)
                else:
                    logger.error("Problem with refresh git %s%s" %
                                 (path, repo))

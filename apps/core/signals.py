#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Year: 2015

from django import dispatch

# send signal after recipe is finished
recipe_finished = dispatch.Signal(providing_args=["recipe"])

# send signal when recipe is changed
recipe_changed = dispatch.Signal(providing_args=["recipe"])

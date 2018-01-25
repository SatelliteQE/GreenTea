#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Pavel Studenik
# Email: pstudeni@redhat.com
# Date: 24.9.2013

import logging
import xml.dom.minidom

from apps.core.models import (Arch, DistroTemplate, JobTemplate,
                              RecipeTemplate, TaskTemplate, Test)

logger = logging.getLogger(__name__)


class Parser:

    def __init__(self, file=None, content=None):
        self.status = True
        try:
            if file:
                self.content_xml = xml.dom.minidom.parse(file)
                self.status = True
            elif content:
                self.content_xml = xml.dom.minidom.parseString(content)
                self.status = True

        except xml.parsers.expat.ExpatError:
            self.error = "%s isn't valid XML file" % file
            logger.error(self.error)
            self.status = False

    def recipe(self, xmlrecipe, is_guestrecipe=None):

        rt = RecipeTemplate(
            jobtemplate=self.job, name=xmlrecipe.getAttribute("whiteboard"))
        if is_guestrecipe:
            rt.is_virtualguest = True
            rt.virtualhost = is_guestrecipe

        distro_family = ""
        distro_variant = ""
        distro_name = ""
        tests = []

        for item in xmlrecipe.childNodes:
            if item.nodeName == "guestrecipe":
                self.recipe(item, is_guestrecipe=rt)
            if item.nodeName == "#text":
                continue
            elif item.nodeName == "task":
                parameters = []
                for param in item.getElementsByTagName("param"):
                    name = param.getAttribute("name")
                    value = param.getAttribute("value")
                    parameters.append((name, value))
                tests.append(
                    [item.getAttribute("name"), parameters, item.getAttribute("role")])

            elif item.nodeName == "hostRequires":
                for key in item.childNodes:
                    if key.nodeName == "#text":
                        continue
                    elif key.nodeName == "labcontroller":
                        op = key.getAttribute("op")
                        value = key.getAttribute("value").lower()
                        rt.labcontroller = "%s %s" % (op, value)
                    elif key.nodeName == "and":
                        for keyvalue in key.childNodes:
                            if keyvalue.nodeName == "#text":
                                continue
                            if keyvalue.nodeName == "#comment":
                                continue
                            name = keyvalue.nodeName
                            value = keyvalue.getAttribute("value")
                            key = keyvalue.getAttribute("key").lower()
                            op = keyvalue.getAttribute("op")
                            if "disk" in (name, key):
                                rt.disk = "%s %s" % (op, value)
                            if "diskspace" in (name, key):
                                rt.disk = "%s %s" % (op, value)
                            if "memory" in (name, key):
                                rt.memory = "%s %s" % (op, value)

            elif item.nodeName == "distroRequires":
                for key in item.childNodes:
                    if key.nodeName == "#text":
                        continue
                    if key.nodeName == "and":
                        for keyvalue in key.childNodes:
                            distronode = keyvalue.nodeName
                            if distronode.startswith("distro"):
                                if distronode.endswith("arch"):
                                    archname = keyvalue.getAttribute("value")
                                elif distronode.endswith("name"):
                                    distro_name = keyvalue.getAttribute(
                                        "value")
                                elif distronode.endswith("variant"):
                                    distro_variant = keyvalue.getAttribute(
                                        "value")
                                elif distronode.endswith("family"):
                                    distro_family = keyvalue.getAttribute(
                                        "value")
                    if key.nodeName == "distro_virt":
                        rt.hmv = True

        rt.distro, status = DistroTemplate.objects.get_or_create(
            name=distro_name, distroname=distro_name,
            variant=distro_variant, family=distro_family)
        rt.kernel_options = xmlrecipe.getAttribute("kernel_options")
        rt.kernel_options_post = xmlrecipe.getAttribute("kernel_options_post")
        rt.ks_meta = xmlrecipe.getAttribute("ks_meta")
        rt.set_role(xmlrecipe.getAttribute("role"))
        rt.save()
        if archname.startswith("CHOOSE_ARCH"):
            sub = archname.replace("x86_64", "x86-64")
            for it in sub.split("_")[2:]:
                it = it.replace("x86-64", "x86_64")
                arch, status = Arch.objects.get_or_create(name=it)
                rt.arch.add(arch)
        else:
            arch, status = Arch.objects.get_or_create(name=archname)
            rt.arch.add(arch)
        counter = 0
        for key, it, role in tests:
            oTest, status = Test.objects.get_or_create(name=key)
            tt = TaskTemplate(test=oTest, recipe=rt)
            tt.priority = counter
            tt.set_role(role)
            for param in it:
                tt.params += "%s=%s\n" % (param[0], param[1])
            tt.save()
            counter += 1
        rt.save()

    def run(self, position=False):
        if not self.status:
            return False
        self.job = None
        for xmljob in self.content_xml.childNodes:
            for it in xmljob.childNodes:
                if it.nodeName == "whiteboard":
                    whiteboard = it.firstChild.nodeValue.strip() if it.firstChild else "(empty)"
                    jt, status = JobTemplate.objects.get_or_create(
                        whiteboard=whiteboard)
                    self.job = jt

                    if position:
                        jt.position = int(position)
                        jt.save()

                elif it.nodeName == "recipeSet":
                    for xmlrecipe in it.childNodes:
                        if xmlrecipe.nodeName == "#text":
                            continue
                        self.recipe(xmlrecipe)

#!/bin/bash

# create default value for running service
RUN python -c 'import random; print "import os\nfrom basic import *\nDEBUG=True\nSECRET_KEY=\"" + "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]) + "\"" ' > greentea/tttt/settings/production.py
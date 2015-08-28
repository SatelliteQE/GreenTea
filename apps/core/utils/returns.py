# created by jstancek@redhat.com

import sys

from django.conf import settings

from bkr.client import conf
from bkr.common.hub import HubProxy


def return_reservation(rid):
    conf['AUTH_METHOD'] = "password"
    conf['HUB_URL'] = 'https://%s' % settings.BEAKER_SERVER
    conf['USERNAME'] = settings.BEAKER_OWNER
    conf['PASSWORD'] = settings.BEAKER_PASS
    hub = HubProxy(conf=conf)
    return hub.recipes.extend(rid, 0)

if __name__ == "__main__":
    return_reservation(sys.argv[1])

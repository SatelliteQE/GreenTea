from tttt.settings.production import *
try:
    from tttt.settings.local import *
except ImportError:
    pass

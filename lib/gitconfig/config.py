import os
from shell import shell
from section import section


class config(object):
    filename = None

    def __init__(self, filename):
        self.filename = os.path.expanduser(filename)

    def __getattr__(self, name):
        return section(self, name)  # called if self.key not exists

    @property
    def sh(self):
        return 'git config --file %s' % self.filename

    def get(self, s, k):
        try:
            return shell(self.sh + " %s.%s" % (s, k))
        except:
            return None

    def set(self, s, k, v):
        shell(self.sh + ' %s.%s "%s"' % (s, k, str(v)))

    def unset(self, s, k):
        try:
            shell(self.sh + " --unset %s.%s" % (s, k))
        except:
            pass

    @property
    def list(self):
        if os.path.exists(self.filename):
            return shell(self.sh + " --list").splitlines()
        else:
            return []

    @property
    def exists(self):
        return os.path.exists(self.filename)

    def delete(self):
        if self.exists:
            os.unlink(self.filename)

    def __str__(self):
        return self.filename
from key import key


class section(object):
    file = None
    _name = None

    def __init__(self, file, name=None):
        self.file = file
        self._name = name

    def __setattr__(self, k, v):
        if hasattr(self, k):
            super(section, self).__setattr__(k, v)

    def __getattribute__(self, k):
        try:  # exists
            return super(section, self).__getattribute__(k)
        except AttributeError:  # not exists
            setattr(section, k, key(k))
            return super(section, self).__getattribute__(k)

    def get(self, k):
        return self.file.get(self._name, k)

    def set(self, k, v):
        return self.file.set(self._name, k, v)

    def unset(self, name):
        self.file.unset(self._name, name)

    def __str__(self):
        return self._name
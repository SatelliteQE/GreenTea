class key(object):
    name = None

    def __init__(self, name):
        self.name = name

    def __get__(self, section, cls):
        return section.get(self.name)

    def __set__(self, section, value):
        section.set(self.name, value)

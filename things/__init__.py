import appscript

class Todo(object):
    _loaded = False
    def __init__(self, raw):
        self.raw = raw
        self._loaded = True

    def __getattr__(self, key):
        if self._loaded:
            return getattr(self.raw, key).get()
        else:
            return self.__dict__[key]

    def __setattr__(self, key, value):
        if self._loaded:
            getattr(self.raw, key).set(value)
        else:
            self.__dict__[key] = value

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "%s (%s)" % (self.name, self.status)

    def is_complete(self):
        return self.status == appscript.k.completed

    def complete(self):
        self.status = appscript.k.completed

    def is_open(self):
        return self.status == appscript.k.open

    def open(self):
        self.status = appscript.k.open

    def is_canceled(self):
        return self.status == appscript.k.canceled

    def cancel(self):
        self.status = appscript.k.canceled

class TodoList(object):
    def __init__(self, raw):
        self.raw = raw
        self.to_dos = [Todo(a) for a in self.raw.to_dos.get()]

class Things(object):
    def __init__(self):
        self.app = appscript.app("Things")
        special = self.app.areas.get() + self.app.people.get()
        regular = [(a.name.get().lower(), a) for a in self.app.lists.get() if a not in special]
        for key, raw_list in regular:
            setattr(self, key, TodoList(raw_list))


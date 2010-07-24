import appscript

class AppleScriptHelper(object):
    """
    Simple object for wrapping AppleScript objects more sanely.

    Each subclass should provide a ``raw`` property that is a property
    from ``appscript``.
    """
    _loaded = False

    def __init__(self):
        self._loaded = True

    def __getattr__(self, key):
        if self._loaded and key != 'set':
            return getattr(self.raw, key).get()
        else:
            return self.__dict__[key]

    def __setattr__(self, key, value):
        if self._loaded:
            if hasattr(self, "set_%s" % key):
                getattr(self, 'set_%s' % key)(value)
            else:
                getattr(self.raw, key).set(value)
        else:
            self.__dict__[key] = value

class TodoAdder(object):
    def add_to_do(self, **kwargs):
        properties = dict([(getattr(appscript.k, key), value) for key, value in kwargs.items()])
        self.raw.make(new=appscript.k.to_do, with_properties=properties)

class TodosProperty(object):
    @property
    def to_dos(self):
        return [Todo(a) for a in self.raw.to_dos.get()]

    def __iter__(self):
        return iter(self.to_dos)


class NamedObject(object):
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, unicode(self))

    def __unicode__(self):
        return u"%s" % self.name.encode('ascii', 'ignore')
    def __str__(self):
        return self.__unicode__()

class DictLikeObject(object):
    def __getitem__(self, key):
        return getattr(self, key)

class TaggableItem(object):
    @property
    def tags(self):
        return TagList(self.raw.tags.get())

    def set_tags(self, tags):
        tags = [tags] if type(tags) is str else tags
        self.raw.tag_names.set(','.join(tags))

    def add_tag(self, tag):
        tags = self.tags
        if tag in tags:
            return
        self.tags = tags + tag

    def remove_tag(self, tag):
        tags = self.tags
        if tag not in tags:
            return
        self.tags = self.tags - tag



class Todo(AppleScriptHelper, NamedObject, TaggableItem):
    OPEN = appscript.k.open
    COMPLETED = appscript.k.completed
    CANCELED = appscript.k.canceled

    def __init__(self, raw):
        self.raw = raw
        AppleScriptHelper.__init__(self)

    def is_complete(self):
        return self.status == Todo.COMPLETED

    def complete(self):
        self.status = Todo.COMPLETED

    def is_open(self):
        return self.status == Todo.OPEN

    def open(self):
        self.status = Todo.OPEN

    def is_canceled(self):
        return self.status == Todo.CANCELED

    def cancel(self):
        self.status = Todo.CANCELED

    def move(self, to_list):
        self.raw.move(to=to_list.raw)

    def __str__(self):
        return "%s (%s)" % (self.name, self.status)

class TodoList(AppleScriptHelper, NamedObject, TodoAdder, TodosProperty):
    def __init__(self, raw):
        self.raw = raw
        AppleScriptHelper.__init__(self)


class ProjectList(AppleScriptHelper, NamedObject, DictLikeObject, TodoAdder):
    def __init__(self, raw):
        self.raw = raw
        for a in self.raw.to_dos.get():
            self.__dict__[a.name.get()] = TodoList(a)
        AppleScriptHelper.__init__(self)

    def __getattr__(self, key):
        try:
            return super(ProjectList, self).__getattr__(key)
        except KeyError:
            return self.__dict__[key]


class SpecialList(AppleScriptHelper, DictLikeObject):
    def __init__(self, raw):
        self.raw = raw
        for area in self.raw.get():
            self.__dict__[area.name.get()] = self.list_of_name(area)

    def __getattr__(self, key):
        try:
            return super(AreaList, self).__getattr__(key)
        except KeyError:
            return self.__dict__[key]

class Area(TodoList):
    pass
class AreaList(SpecialList):
    list_of_name = Area
    pass


class Person(TodoList):
    pass
class PeopleList(SpecialList):
    list_of_name = Person
    pass

class Tag(AppleScriptHelper, NamedObject, TodosProperty):
    def __init__(self, raw):
        self.raw = raw
        super(Tag, self).__init__()

    @property
    def parent_tag(self):
        raw = self.raw.parent_tag.get()
        return None if raw == appscript.k.missing_value else Tag(raw)

class TagList(DictLikeObject):
    def __init__(self, raw):
        for tag in raw:
            self.__dict__[tag.name.get()] = Tag(tag)
        super(TagList, self).__init__()

    def __contains__(self, k):
        return k in self.__dict__

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, unicode(self.__dict__))

    def __add__(self, k):
        k = [k, ] if type(k) is str else k
        return self.values() + k

    def __sub__(self, k):
        k = [k, ] if type(k) is str else k
        values = self.values()
        [values.remove(a) for a in k]
        return values

    def values(self):
        return [a.name for a in self.__dict__.values()]


class Things(AppleScriptHelper, TodoAdder):
    def __init__(self):
        self.raw = appscript.app("Things")
        special = self.raw.areas.get() + self.raw.people.get()
        regular = [(a.name.get().lower(), a) for a in self.raw.lists.get() if a not in special]
        for key, raw_list in regular:
            if key == "projects":
                setattr(self, key, ProjectList(raw_list))
            else:
                setattr(self, key, TodoList(raw_list))
        self.tags = TagList(self.raw.tags.get())
        self.areas = AreaList(self.raw.areas)
        self.people = PeopleList(self.raw.people)
        super(Things, self).__init__()


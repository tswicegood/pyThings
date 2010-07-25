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
        return self._internal[key]

class TaggableItem(object):
    @property
    def tags(self):
        return TagList(self.raw.tags, item=self)

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


class EditableItem(object):
    def edit(self):
        self.raw.edit()


class Todo(AppleScriptHelper, NamedObject, TaggableItem, EditableItem):
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


class Project(AppleScriptHelper, NamedObject, TodoAdder, TodosProperty, TaggableItem, EditableItem):
    def __init__(self, raw):
        self.raw = raw
        AppleScriptHelper.__init__(self)

class ProjectList(AppleScriptHelper, NamedObject, DictLikeObject, TodoAdder):
    def __init__(self, raw):
        self.raw = raw
        self._internal = {}
        for a in self.raw.to_dos.get():
            self._internal[a.name.get()] = Project(a)
        AppleScriptHelper.__init__(self)

    def __getattr__(self, key):
        try:
            return super(ProjectList, self).__getattr__(key)
        except KeyError:
            if key in self.__dict__:
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
        AppleScriptHelper.__init__(self)

    @property
    def parent_tag(self):
        raw = self.raw.parent_tag.get()
        return None if raw == appscript.k.missing_value else Tag(raw)

    def delete(self):
        self.raw.delete()

    class NotFoundError(Exception):
        def __init__(self, name):
            msg = "Unable to locate tag '%s', perhaps try creating it via Things().add_tag(name='%s')" % (name, name)
            super(Tag.NotFoundError, self).__init__(msg)


class TagList(DictLikeObject):
    def __init__(self, raw, item=False):
        self.item = item
        self.raw = raw
        self._internal = {}
        raw = raw if type(raw) is list else raw.get()
        for tag in raw:
            self._internal[tag.name.get()] = Tag(tag)
        super(TagList, self).__init__()

    def __getitem__(self, k):
        try:
            return DictLikeObject.__getitem__(self, k)
        except KeyError:
            raise Tag.NotFoundError(k)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, unicode(self._internal))

    def __contains__(self, k):
        return k in self._internal

    def __add__(self, k):
        if self.item:
            k = [k, ] if type(k) is str else k
            self.item.tags = self.values() + k
        else:
            new(Things.app, appscript.k.tag, name=k)
    def __sub__(self, k):
        self.__handle_removal(k)

    def __delitem__(self, k):
        self.__handle_removal(k)

    def __handle_removal(self, k):
        if self.item:
            self.remove_tag(k)
        else:
            self.delete_tag(k)

    def remove_tag(self, tag_name):
        tag_name = [tag_name, ] if type(tag_name) is str else tag_name
        values = self.values()
        [values.remove(a) for a in tag_name]
        return values


    def delete_tag(self, tag_name):
        try:
            tag = self._internal[tag_name]
            del self._internal[tag_name]
            tag.delete()
        except KeyError:
            raise Tag.NotFoundError(tag_name)

    def values(self):
        return [a.name for a in self._internal.values()]


class Things(AppleScriptHelper, TodoAdder):
    app = appscript.app("Things")
    def __init__(self):
        self.raw = Things.app
        special = self.raw.areas.get() + self.raw.people.get()
        regular = [(a.name.get().lower(), a) for a in self.raw.lists.get() if a not in special]
        for key, raw_list in regular:
            if key == "projects":
                setattr(self, key, ProjectList(raw_list))
            else:
                setattr(self, key, TodoList(raw_list))
        self.areas = AreaList(self.raw.areas)
        self.people = PeopleList(self.raw.people)
        super(Things, self).__init__()

    @property
    def tags(self):
        return TagList(self.raw.tags)

    # This is necessary to avoid an exception using the += syntax to add a new
    # system-level tag.
    def set_tags(self, *args):
        return self.tags

    def new_tag(self, **kwargs):
        return Tag(new(self.raw, appscript.k.tag, **kwargs))

    def new_to_do(self, **kwargs):
        return Todo(new(self.raw, appscript.k.to_do, **kwargs))

    @property
    def selected(self):
        return [Todo(a) for a in self.raw.selected_to_dos.get()]


def new(app, type, **kwargs):
    properties = dict([(getattr(appscript.k, key), value) for key, value in kwargs.items()])
    return app.make(new=type, with_properties=properties)



from . import basics
from .. import utils

def is_inferred_sequence(node):
    return isinstance(node, (InferredList, InferredTuple))

class BaseCompoundType(basics.InferredType):
    """This is the base class for other classes that can hold other objects"""
    def __init__(self):
        super().__init__()
        self.items = basics.TypeSet()

    def get_item(self, index):
        return self.items

    def get_iter(self):
        return self.get_item(-1)

    def get_slice_from(self, index):
        return [*self.items]

    def add_item(self, item):
        assert(basics.is_inferred_type(item))
        self.items = self.items.add_type(item)

    def get_star_expansion(self):
        return [self.items] * 4
        
    def __hash__(self):
        return id(self)



class InferredList(BaseCompoundType):
    def __init__(self, *args):
        super().__init__()
        self.name = "<list>"
        for arg in args:
            self.add_item(arg)

    @utils.do_not_recurse('[...]')
    def __str__(self):
        return '[%s]' % self.items

class InferredSet(BaseCompoundType):
    def __init__(self, *args):
        super().__init__()
        self.name = "<set>"
        for arg in args:
            self.add_item(arg)

    @utils.do_not_recurse('[...]')
    def __str__(self):
        return '{%s}' % self.items

class InferredFrozenSet(InferredSet):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = "<frozenset>"

class InferredTuple(BaseCompoundType):
    def __init__(self, *args):
        super().__init__()
        self.name = "<tuple>"
        self.items = list(args)

    @utils.do_not_recurse('(...)')
    def __str__(self):
        item_names = [str(x) for x in self.items]
        return"({})".format(', '.join(item_names))

    def add_item(self, item):
        pass

    def get_item(self, index):
        if basics.is_inferred_type(index):
            return basics.TypeSet(*self.items)
        try:
            return self.items[index]
        except IndexError:
            return basics.UnknownType()

    def get_slice(self):
        return [*self.items]

    def get_iter(self):
        return basics.TypeSet(*self.items)

    def get_slice_from(self, index):
        return [*self.items[index:]]

    def get_star_expansion(self):
        return self.items


class InferredDict(BaseCompoundType):
    def __init__(self, keys=None, values=None):
        super().__init__()
        self.name = "<dict>"
        if keys is None:
            keys = []
        if values is None:
            values = []
        self.keys = basics.TypeSet(*keys)
        self.items = basics.TypeSet(*values)

    def __str__(self):
        return "{{{!s}: {!s}}}".format(self.keys, self.items)

    def get_key(self):
        return self.keys

    def get_iter(self):
        return self.get_key()

class InferredIterator(BaseCompoundType):
    def __init__(self, return_type):
        super().__init__()
        self.add_item(return_type)

    def __str__(self):
        return "(-> {!s})".format(self.items)



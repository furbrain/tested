import itertools
from .. import utils

def is_inferred_type(node):
    return isinstance(node, (InferredType, TypeSet))

def get_type_name(obj):
    if isinstance(obj, type):
        return obj.__name__
    else:
        if obj is None:  # Special case for NoneType which is weird
            return 'None'
        else:
            return '<{}>'.format(type(obj).__name__)

class InferredType():
    @classmethod
    def from_type(cls, object_type):
        self = cls()
        self.type = object_type
        self.name = get_type_name(object_type)
        return self

    def __init__(self):
        self.attrs = {}
        self.items = TypeSet()
        self.name = ""
        self.docstring = ""

    @utils.do_not_recurse('...')
    def __str__(self):
        return self.name

    @utils.do_not_recurse('...')
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, InferredType):
            return str(self) == str(other)
        elif isinstance(other, TypeSet) and len(other) == 1:
            return self in other
        elif isinstance(other, str):
            return str(self) == other
        elif isinstance(other, type):
            return self.type == other
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.name)

    def __iter__(self):
        return iter((self,))

    def has_attr(self, attr):
        assert(isinstance(attr, str))
        return attr in self.attrs

    def get_attr(self, attr):
        if attr not in self.attrs:
            self.attrs[attr] = UnknownType()
        return self.attrs[attr]

    def set_attr(self, attr, typeset):
        assert(is_inferred_type(typeset))
        self.attrs[attr] = typeset

    def add_attr(self, attr, typeset):
        assert(is_inferred_type(typeset))
        if attr in self.attrs:
            self.attrs[attr] = self.attrs[attr].add_type(typeset)
        else:
            self.attrs[attr] = typeset

    def get_item(self, index):
       return UnknownType()

    def get_iter(self):
       return UnknownType()

    def get_slice_from(self, index):
       return [UnknownType()]

    def add_item(self, item):
        pass
        
    def get_call_return(self, arg_types):
        assert(all(is_inferred_type(x) for x in arg_types))
        if "__call__" in self.attrs:
            return self.attrs['__call__'].get_call_return(arg_types)
        else:
            return UnknownType()

    def add_type(self, other):
        assert(is_inferred_type(other))
        if self == other:
            return self
        return TypeSet(self, other)

    def get_all_attrs(self):
        return self.attrs.copy()

    def get_star_expansion(self):
        return [UnknownType()]

class UnknownType(InferredType):
    def __init__(self, name=None):
        super().__init__()
        if name:
            self.name = "Unknown: %s" % name
            self.type = name
        else:
            self.name = "Unknown"
            self.type = ""

class TypeSet():
    def __init__(self, *args):
        self.types = set()
        for a in args:
            self.add_type(a)

    def add_type(self, other):
        if isinstance(other, TypeSet):
            self.types.update(other)
        elif is_inferred_type(other):
            self.types.add(other)
        else:
            self.types.add(InferredType.from_type(other))
        return self

    def get_attr(self, attr):
        return TypeSet(*[tp.get_attr(attr) for tp in self.types])

    def add_attr(self, attr, typeset):
        assert(is_inferred_type(typeset))
        for tp in list(self.types):
            tp.add_attr(attr, typeset)

    def has_attr(self, attr):
        return any(tp.has_attr(attr) for tp in self.types)

    def get_item(self, index):
        return TypeSet(*[tp.get_item(index) for tp in self.types])

    def add_item(self, item):
        assert(is_inferred_type(item))
        for tp in list(self.types):
            tp.add_item(item)

    def get_iter(self):
        return TypeSet(*[tp.get_iter() for tp in self.types])

    def get_call_return(self, arg_types):
        assert(all(is_inferred_type(x) for x in arg_types))
        return TypeSet(*[tp.get_call_return(arg_types) for tp in self.types])

    def get_all_attrs(self):
        results = {}
        for tp in self.types:
            new_attrs = tp.get_all_attrs()
            for key, value in new_attrs.items():
                if key in results:
                    results[key] = results[key].add_type(value)
                else:
                    results[key] = value
        return results

    def get_star_expansion(self):
        items = [tp.get_star_expansion() for tp in self.types]
        transposed_items = list(itertools.zip_longest(*items))
        stripped_items = [[y for y in x if y is not None] for x in transposed_items]
        items = [TypeSet(*args) for args in stripped_items]
        return items

    def __str__(self):
        return ' | '.join(sorted(str(x) for x in self.types))

    def __repr__(self):
        return "<TypeSet: %s>" % self

    def __iter__(self):
        return iter(self.types)

    def __eq__(self, other):
        if isinstance(other, TypeSet):
            return self.types == other.types
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self.types)

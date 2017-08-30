import inspect
import re

def get_type_name(obj):
    if inspect.isclass(obj):
        return obj.__name__
    else:
        if obj is None: # Special case for NoneType which is weird
            return 'None'
        else:
            return '<{}>'.format(type(obj).__name__)

class InferredType():
    @classmethod
    def fromType(cls, object_type):
        self = cls()
        self.type = object_type
        self.name = get_type_name(object_type)
        return self
        
    def __init__(self):
        self.attrs = {}
        self.items = TypeSet()
        self.args = []
        self.return_values = None
        self.name=""
        self.docstring=""
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return str(self)
        
    def __eq__(self, other):
        if isinstance(other,InferredType):
            return str(self)==str(other)
        elif isinstance(other, TypeSet) and len(other)==1:
            return self in other
        elif isinstance(other, str):
            return str(self)==other
        elif inspect.isclass(other):
            return self.type == other
        else:
            return NotImplemented
            
    def __ne__(self,other):
        return not self==other
                        
    def __hash__(self):
        return hash(self.name)
        
    def __iter__(self):
        return iter((self,))
        
    def has_attr(self, attr):
        return attr in self.attrs
        
    def get_attr(self, attr):
        if attr not in self.attrs:
            self.attrs[attr] = UnknownType()
        return self.attrs[attr]
        
    def add_attr(self, attr, typeset):
        if attr in self.attrs:
            self.attrs[attr] = self.attrs[attr].add_type(typeset)
        else:
            self.attrs[attr] = typeset
            
    def get_item(self, index):
        if self.items:
            return self.items
        else:
            return UnknownType()
            
    def add_item(self, item):
        self.items = self.items.add_type(item)
        
    def get_call_return(self, arg_types):
        if "__call__" in self.attrs:
            return self.attrs['__call__'].get_call_return(arg_types)
        if self.return_values:
            return_typeset = TypeSet()
            type_mapping = {k:v for k,v in zip(self.args, arg_types)}
            for possible_type in self.return_values:
                if isinstance(possible_type,UnknownType):
                    replacement_type = type_mapping.get(possible_type.type, UnknownType())
                    return_typeset =return_typeset.add_type(replacement_type)
                else:
                    return_typeset = return_typeset.add_type(possible_type)
            return return_typeset
        return UnknownType()

    def add_type(self, other):
        if self==other:
            return self
        return TypeSet(self, other)
        
class UnknownType(InferredType):
    def __init__(self, name=None):
        if name:
            self.name = "Unknown: %s" % name
            self.type = name
        else:
            self.name = "Unknown"
            self.type = ""

class InferredList(InferredType):
    def __init__(self, *args):
        super().__init__()
        self.name="list"
        for arg in args:
            self.add_item(arg)
        
    def __str__(self):
        return '[%s]' % self.items

class TypeSet():
    def __init__(self, *args):
        self.types = set()
        for a in args:
            self.add_type(a)

    def add_type(self, other):
        if isinstance(other,TypeSet):
            self.types.update(other)
        elif isinstance(other,(InferredType, InferredList)):
            self.types.add(other)
        else:
            self.types.add(InferredType.fromType(other))
        return self
            
    def get_attr(self, attr):
        return TypeSet(*[tp.get_attr(attr) for tp in self.types])
        
    def add_attr(self, attr, typeset):
        for tp in self.types:
            tp.add_attr(attr, typeset)

    def get_item(self, index):
        return TypeSet(*[tp.get_item(index) for tp in self.types])
            
    def add_item(self, item):
        for tp in self.types:
            tp.add_item(item)
        
    def get_call_return(self, arg_types):
        return TypeSet(*[tp.get_call_return(arg_types) for tp in self.types])


    def __str__(self):
        return ', '.join(sorted(str(x) for x in self.types))
        
    def __repr__(self):
        return "<TypeSet: (%s)>" % self
        
    def __iter__(self):
        return iter(self.types)
        
    def __eq__(self, other):
        if isinstance(other,TypeSet):
            return self.types==other.types
        if isinstance(other,str):
            return str(self)==other
        return NotImplemented
        
    def __ne__(self, other):
        return not self==other
        
    def __len__(self):
        return len(self.types)
        
    def __getitem__(self, index):
        return sorted(list(self.types))[index]

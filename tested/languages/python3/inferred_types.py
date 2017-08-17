import inspect

class InferredType():
    def __init__(self, tp):
        if inspect.isclass(tp):
            self.type = tp
        else:
            self.type = type(tp)
        self.name = self.type.__name__
        self.attrs = {}
        self.items = TypeSet()
        
    def __str__(self):
        return self.name
        
    def __eq__(self, other):
        if isinstance(other,InferredType):
            return self.type == other.type
        elif inspect.isclass(other):
            return self.type == other
        else:
            return False
            
    def __ne__(self,other):
        return not self==other
                        
    def __hash__(self):
        return hash(self.name)
        
    def get_attr(self, attr):
        return self.attrs.get(attr,TypeSet(UnknownType()))
        
    def add_attr(self, attr, typeset):
        if attr in self.attrs:
            self.attrs[attr].add(typeset)
        else:
            self.attrs[attr] = typeset
            
    def get_item(self, index):
        if self.items:
            return self.items
        else:
            return TypeSet(UnknownType())
            
    def add_item(self, item):
        self.items.add(item)

class UnknownType(InferredType):
    def __init__(self, name=None):
        if name:
            self.name = "Unknown: %s" % name
            self.type = name
        else:
            self.name = "Unknown"
            self.type = ""

class InferredList():
    def __init__(self, *args):
        self.element_types = TypeSet()
        for arg in args:
            self.add(arg)
        
    def add(self, other):
        self.element_types.add(other)
    
    def __str__(self):
        return '[%s]' % self.element_types

class TypeSet():
    def __init__(self, *args):
        self.types = set()
        for a in args:
            self.add(a)

    def add(self, other):
        if isinstance(other,TypeSet):
            self.types.update(other)
        elif isinstance(other,(InferredType, InferredList)):
            self.types.add(other)
        else:
            self.types.add(InferredType(other))
            
    def matches(self, type_list):
        return any(x in type_list for x in self.types)        
            
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
        return False
        
    def __ne__(self, other):
        return not self==other
        
    def __len__(self):
        return len(self.types)

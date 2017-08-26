import inspect
import re

class InferredType():
    @classmethod
    def fromType(cls, object_type):
        self = cls()
        if inspect.isclass(object_type):
            self.type = object_type
        else:
            self.type = type(object_type)
        self.name = self.type.__name__
        return self
        
    @classmethod
    def fromString(cls, text):
        type_pattern = r"^([\w.]+)$"
        type_match = re.match(type_pattern, text)
        if type_match:
            return InferredType.fromType(eval(type_match.group(1)))

        func_pattern = r"""(?x)
        ^(?P<func_name>\w+)                # function name
        \( (?P<args>(\w+[, ]*)*) \)\s*->\s* # argument list and arrow
        \( (?P<result>(\w+[, ]*)+) \)$        # result list"""
        func_match = re.match(func_pattern, text, re.VERBOSE)
        if func_match:
            from .functions import FunctionType
            name = func_match.group('func_name')
            args = func_match.group('args')
            result = func_match.group('result')
            it = FunctionType(name = name,
                              args = [x.strip() for x in args.split(',')],
                              returns = TypeSet(*[InferredType.fromString(x.strip()) for x in result.split(',')]),
                              docstring = "")
            return it
            

    def __init__(self):
        self.attrs = {}
        self.items = TypeSet()
        self.call_response = lambda x: TypeSet(UnknownType())
        self.name=""
        
    def __str__(self):
        return self.name
        
    def __eq__(self, other):
        if isinstance(other,InferredType):
            return self.name == other.name
        elif inspect.isclass(other):
            return self.type == other
        else:
            return False
            
    def __ne__(self,other):
        return not self==other
                        
    def __hash__(self):
        return hash(self.name)
        
    def get_attr(self, attr):
        if attr not in self.attrs:
            self.attrs[attr] = TypeSet(UnknownType())
        return self.attrs[attr]
        
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
        
    def get_call_return(self, arg_types):
        return self.call_response(arg_types)

    def set_call_return_func(self, func):
        self.call_response = func
        
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
            self.add(a)

    def add(self, other):
        if isinstance(other,TypeSet):
            self.types.update(other)
        elif isinstance(other,(InferredType, InferredList)):
            self.types.add(other)
        else:
            self.types.add(InferredType.fromType(other))
            
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
        
    def __getitem__(self, index):
        return sorted(list(self.types))[index]

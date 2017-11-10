import os.path

from . import inferred_types, signatures

BUILTIN_TYPES = (int, bool, float, complex, str, bytes, bytearray, list, tuple, range, set, frozenset, dict, type(None), type)

_scope = None

def get_built_in_for_literal(value):
    type_name = inferred_types.get_type_name(value)
    return get_built_in_type(type_name)
    
def get_built_in_type(text):
    scp = get_global_scope()
    if text not in scp:
        raise AttributeError('Unknown builtin type {}'.format(text))
    return scp[text]

def get_global_scope():
    global _scope    
    if _scope is None:
        _scope = create_scope()
    return _scope
    
def create_list(*items):
    list_type = get_built_in_type('list')
    return list_type.get_new_instance(*items)

def create_set(*items):
    set_type = get_built_in_type('set')
    return set_type.get_new_instance(*items)

def create_tuple(*items):
    tuple_type = get_built_in_type('tuple')
    return tuple_type.get_new_instance(*items)

def create_dict(keys, values):
    dict_type = get_built_in_type('dict')
    return dict_type.get_new_instance(keys, values)
    
def create_scope():
    from .classes import ClassType
    scope={}
    for tp in BUILTIN_TYPES:
        if tp.__name__ in SpecialTypeClass.TYPES:
            class_type = SpecialTypeClass(tp.__name__)
        else:
            class_type = ClassType(tp.__name__, [])
        scope[class_type.name] = class_type
        instance_type = class_type.instance_type
        if tp.__name__ == "NoneType":
            instance_type.name = "None"
        scope[instance_type.name] = instance_type
    scope['<None>'] = scope['None']
    for tp in BUILTIN_TYPES:
        sig_filename = os.path.join(os.path.dirname(__file__), 'specs', tp.__name__+'.spec')
        with open(sig_filename, 'r') as sig_file:
            for name, attr in signatures.read_spec(sig_file.read(), scope).items():
                scope[tp.__name__].add_attr(name, attr)            
    return scope        
    
    
class SpecialTypeClass(inferred_types.InferredType):
    TYPES = {
        'list': inferred_types.InferredList,
        'tuple': inferred_types.InferredTuple,
        'dict': inferred_types.InferredDict,
        'set': inferred_types.InferredSet,
        'frozenset': inferred_types.InferredFrozenSet
    }
    
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.subtype = self.TYPES[name]
        self.instance_type = self.subtype()
        
    def add_attr(self, attr, typeset):
        super().add_attr(attr, typeset)
        self.instance_type.add_attr(attr, typeset)

    def get_call_return(self, arg_types):
        return self.get_new_instance()

    def get_new_instance(self, *args):
        copy = self.subtype(*args)
        copy.attrs = self.attrs.copy()
        return copy

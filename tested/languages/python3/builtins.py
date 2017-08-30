from .inferred_types import InferredType, get_type_name
from .magic_functions import add_all_magic_functions
BASIC_TYPES = (1, 2.0, True, complex(1,2), "abc", None)

_scope = None

def get_built_in_for_literal(value):
    scp = get_global_scope()
    type_name = get_type_name(value)
    if type_name not in scp:
        raise AttributeError('Unknown builtin type {}'.format(type_name))
    return scp[type_name]

def get_global_scope():
    global _scope    
    if _scope is None:
        _scope = create_scope()
    return _scope
    
def create_scope():
    scope = {}
    for tp in BASIC_TYPES:
        instance_type = InferredType.fromType(tp)
        scope[instance_type.name] = instance_type
        class_type = InferredType.fromType(tp.__class__)
        scope[class_type.name] = class_type
    for tp in BASIC_TYPES:
        add_all_magic_functions(scope, tp)
    return scope
        
    

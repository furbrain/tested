from .inferred_types import InferredType, get_type_name
from .utils.get_signatures import BUILTIN_TYPES

_scope = None

def get_built_in_for_literal(value):
    type_name = get_type_name(value)
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
    
def create_scope():
    scope={}
    for tp in BUILTIN_TYPES:
        try:
            instance_type = InferredType.fromType(tp())
        except TypeError:
            instance_type = InferredType.fromType(tp(0))
        scope[instance_type.name] = instance_type
        class_type = InferredType.fromType(tp)
        scope[class_type.name] = class_type
    scope['<None>'] = scope['None']
    print(scope)
    return scope        
    

from .inferred_types import InferredType
from .magic_functions import add_all_magic_functions, get_instance_name_from_type
BASIC_TYPES = (1, 2.0, True, complex(1,2), "abc", None)

_scope = None
                
def get_global_scope():
    global _scope    
    if _scope is None:
        _scope = create_scope()
    return _scope
    
def create_scope():
    scope = {}
    for tp in BASIC_TYPES:
        new_type = InferredType.fromType(tp)
        new_type.name = get_instance_name_from_type(tp)
        scope[get_instance_name_from_type(tp)] = new_type
    for tp in BASIC_TYPES:
        add_all_magic_functions(scope, tp)
    return scope
        
    

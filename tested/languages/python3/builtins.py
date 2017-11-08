import os.path

from .inferred_types import InferredType, get_type_name
from .utils.get_signatures import BUILTIN_TYPES
from .signatures import read_spec

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
    from .classes import ClassType
    scope={}
    for tp in BUILTIN_TYPES:
        class_type = ClassType(tp.__name__,[])
        scope[class_type.name] = class_type
        instance_type = class_type.instance_type
        if tp.__name__ == "NoneType":
            instance_type.name="None"
        scope[instance_type.name] = instance_type
    scope['<None>'] = scope['None']
    for tp in BUILTIN_TYPES:
        sig_filename = os.path.join(os.path.dirname(__file__), 'specs', tp.__name__+'.spec')
        with open(sig_filename,'r') as sig_file:
            for name, attr in read_spec(sig_file.read(), scope).items():
                scope[tp.__name__].add_attr(name, attr)            
    return scope        
    

from .inferred_types import InferredType, get_type_name
from .magic_functions import add_all_magic_functions, add_functions


# Extra methods for the builtin types: key is return value, value is string with all func names
INT_FUNCS = {'<int>':'bit_length conjugate from_bytes',
             '<bytes>':'to_bytes'}
FLOAT_FUNCS=  { '<float>':'conjugate from_hex',
                '<bool>':'is_integer',
                '<str>':'hex'}
###FIXME### add integer ratio???
BOOL_FUNCS = INT_FUNCS
COMPLEX_FUNCS = {'<complex>':'conjugate',
                 '<float>':'__abs__'} #patch abs to give float from complex...
STR_FUNCS = {'<str>':'''capitalize casefold center expandtabs format format_map join ljust 
                        lower lstrip replace rjust rstrip strip swapcase title translate upper zfill''',
             '<int>':'count find index rfind rindex',
             '<bool>':'''endswith isalnum isalpha isdecimal isdigit isidentifier islower isnumeric
                         isprintable isspace istitle isupper startswith''',
             '<bytes>':'encode'}
BYTES_FUNCS = {'<bytes>': '''capitalize center expandtabs fromhex join ljust lower lstrip 
                             replace rjust rstrip strip swapcase title translate upper zfill''',
               '<int>':'''count find hex index rfind rindex''',
               '<bool>':'''endswith isalnum isalpha isdigit islower isspace istitle isupper startswith''',
               '<str>':'''decode'''}
NONE_FUNCS = {}
##FIXME## add partition rpartition and split rsplit and splitlines maketable for bytes and str
BASIC_TYPES = {5: INT_FUNCS, 
               2.0: FLOAT_FUNCS, 
               True: BOOL_FUNCS, 
               complex(1,2): COMPLEX_FUNCS, 
               "abc": STR_FUNCS, 
               b'abc': BYTES_FUNCS, 
               None: NONE_FUNCS}

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
    scope = {}
    
    for tp in BASIC_TYPES:
        instance_type = InferredType.fromType(tp)
        scope[instance_type.name] = instance_type
        class_type = InferredType.fromType(tp.__class__)
        scope[class_type.name] = class_type
    for tp in BASIC_TYPES:
        add_all_magic_functions(scope, tp)
    cmpl = scope['<complex>']
    for tp, func_lists in BASIC_TYPES.items():
        instance_type = scope[get_type_name(tp)]
        class_type = scope[get_type_name(tp.__class__)]
        for ret_val,func_list in func_lists.items():
            add_functions(instance_type, func_list, scope[ret_val], is_magic=False)
            add_functions(class_type, func_list, scope[ret_val], is_magic=False)    
    return scope
        
    

from .functions import FunctionType
from .inferred_types import UnknownType

BOOL_FUNCS = '''bool contains eq ge gt le lt ne'''
INT_FUNCS = '''cmp hash index int len rcmp'''
FLOAT_FUNCS = '''float'''
STR_FUNCS = '''hex repr str'''
COMPLEX_FUNCS = '''complex'''
REFLEX_FUNCS = '''abs add and div floordiv iadd iand idiv ifloordiv ilshift imod imul
                  invert ior ipow irshift isub ixor lshift mod mul neg or pos pow
                  radd rand rdiv rfloordiv rlshift rmod rmul ror rpow rrshift rshift rsub
                  rxor sub'''
NONE_FUNCS = '''del delattr delete delitem delslice set setattr setitem setslice'''
UNKNOWN_FUNCS = '''call get getattr getattribute getitem getslice'''
NONE_TYPE = type(None)
FUNC_TYPES = {
    True: BOOL_FUNCS,
    1: INT_FUNCS,
    2.0: FLOAT_FUNCS,
    "abc": STR_FUNCS,
    complex(1,2): COMPLEX_FUNCS,
    None: NONE_FUNCS,
    }

def get_instance_name_from_type(tp):
    if hasattr(tp,'__name__'):
        return "<{}>".format(tp.__name__)
    else:
        return "<{}>".format(tp.__class__.__name__)
    
            
def add_all_magic_functions(scope, tp):
    tp = scope[get_instance_name_from_type(tp)]
    for return_type, func_list in FUNC_TYPES.items():
        add_magic_functions(tp, func_list, scope[get_instance_name_from_type(return_type)])
    add_magic_functions(tp, REFLEX_FUNCS, tp.type)
    add_magic_functions(tp, UNKNOWN_FUNCS, UnknownType())
    
def add_magic_functions(tp, function_list, return_type):
    for func in function_list.split():
        func_name = "__{}__".format(func)
        if hasattr(tp.type,func_name):
            function = FunctionType.fromFunction(getattr(tp.type,func_name), return_type)
            tp.add_attr(func_name, function)


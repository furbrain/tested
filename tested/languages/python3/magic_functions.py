from .functions import FunctionType
from .inferred_types import UnknownType, get_type_name

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
    5: INT_FUNCS,
    2.0: FLOAT_FUNCS,
    "abc": STR_FUNCS,
    complex(1,2): COMPLEX_FUNCS,
    None: NONE_FUNCS,
    }

def add_all_magic_functions(scope, tp):
    class_tp = scope[get_type_name(tp.__class__)]
    instance_tp = scope[get_type_name(tp)]
    for tp in (class_tp, instance_tp):
        for return_type, func_list in FUNC_TYPES.items():
            add_functions(tp, func_list, scope[get_type_name(return_type)])
            add_functions(instance_tp, func_list, scope[get_type_name(return_type)])
        add_functions(tp, REFLEX_FUNCS, instance_tp)
        add_functions(tp, UNKNOWN_FUNCS, UnknownType())
    
        
def add_functions(tp, function_list, return_type, is_magic=True):
    for func in function_list.split():
        if is_magic:
            func = "__{}__".format(func)
        if hasattr(tp.type,func):
            function = FunctionType.fromFunction(getattr(tp.type,func), return_type)
            tp.add_attr(func, function)


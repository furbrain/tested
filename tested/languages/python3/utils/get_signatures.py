#!/usr/bin/python3
import inspect
import re


BOOL_FUNCS = '''bool contains eq ge gt le lt ne subclasshook'''
INT_FUNCS = '''cmp hash index int len rcmp sizeof'''
FLOAT_FUNCS = '''float'''
STR_FUNCS = '''format hex repr str'''
COMPLEX_FUNCS = '''complex'''
REFLEX_FUNCS = '''abs add and div floordiv iadd iand idiv ifloordiv ilshift imod imul
                  invert ior ipow irshift isub ixor lshift mod mul neg new or pos pow
                  radd rand rdiv rfloordiv rlshift rmod rmul ror rpow rrshift rshift rsub
                  rxor sub'''
NONE_FUNCS = '''del delattr delete delitem delslice init set setattr setitem setslice'''
UNKNOWN_FUNCS = '''call get getattr getattribute getitem getslice'''
NONE_TYPE = type(None)

def make_dunderlist(text):
    return re.sub(r"\b","__",text).split()

FUNC_TYPES = {
    'bool': make_dunderlist(BOOL_FUNCS),
    'int': make_dunderlist(INT_FUNCS),
    'float': make_dunderlist(FLOAT_FUNCS),
    'str': make_dunderlist(STR_FUNCS),
    'complex': make_dunderlist(COMPLEX_FUNCS),
    'None': make_dunderlist(NONE_FUNCS),
    '[str]': ['__dir__'],
    }

    
def get_retval(name, type_name):
    for retval, func_list in FUNC_TYPES.items():
        if name in func_list:
            return retval
    if name in make_dunderlist(REFLEX_FUNCS):
        return type_name
    return None
    
BUILTIN_TYPES = (int, bool, float, complex, str, bytes, bytearray, list, tuple, range, set, frozenset, dict, NONE_TYPE, type)
FUNC_PATTERN = r"""(?x)
              (?:\w\.)?(?P<name>\w+) \s*    # function name
              \( (?P<args>.*) \)   # arguments
              \s* -> \s*           # arrow
              (?P<retval>.*)    # return value"""


if __name__=="__main__":
    for tp in BUILTIN_TYPES:
        fname = "../specs/{}.spec".format(tp.__name__)
        with open(fname, 'w') as f:
            for name, obj in inspect.getmembers(tp):
                if inspect.isroutine(obj):
                    args = []
                    retval = None
                    try:
                        argspec = inspect.getfullargspec(obj)
                        args = argspec.args
                    except TypeError:
                        if obj.__doc__:
                            docline =obj.__doc__.splitlines()[0]
                            match = re.match(FUNC_PATTERN, docline)
                            if match:
                                args = match.group('args').split(',')
                                retval = match.group('retval')
                    retval = get_retval(name, tp.__name__) or retval or "Unknown"
                    args = ', '.join(x.strip() for x in args)
                    args = re.sub(r'\[|\]|=\s*\w+\s*','',args)
                    args = args.replace(']','')
                    f.write('{name}({args}) -> {retval}\n'.format(name=name, args=args, retval=retval))
                elif inspect.isdatadescriptor(obj) or inspect.ismethoddescriptor(obj):
                    f.write('{name} = Unknown\n'.format(name=name))
                elif isinstance(obj, BUILTIN_TYPES):
                    f.write('{name} = {tp}\n'.format(name=name, tp = obj.__class__.__name__))
                    f.write('\n')
                    continue
                if obj.__doc__:
                    for line in obj.__doc__.splitlines():
                        f.write('  {}\n'.format(line))
                f.write('\n')
                    
                    

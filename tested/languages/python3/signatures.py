import re
from . import inferred_types
from . import functions
from . import classes
from . import builtins

def split_on(text, split):
    """return a string split on "split" characters provided they are not within brackets"""
    bracket_queue = []
    brackets = {'}':'{', 
                ']':'[',
                ')':'(',
                '>':'<'}
    result = [""]
    for i, char in enumerate(text):
        if char in brackets.values():
            bracket_queue.append(char)
        if char in brackets.keys():
            if bracket_queue and brackets[char]==bracket_queue[-1]:
                bracket_queue.pop()
            else:
                raise AttributeError('Unmatched bracket')
        if char==split and len(bracket_queue)==0:
            result.append("")
        else:
            result[-1] += char
    return result

def is_bracketed(text,brackets):
    return text[0]==brackets[0] and text[-1]==brackets[-1]

def read_type(text):
    text = text.strip()
    #first split on pipes...
    pipes = split_on(text, '|')
    if len(pipes)>1:
        subtypes = [read_type(x) for x in pipes]
        return inferred_types.TypeSet(*subtypes)
    text = pipes[0].strip()

    #return tuples
    if is_bracketed(text,'()'):
        text = text[1:-1]
        subtypes = [read_type(x) for x in split_on(text, ',')]
        return inferred_types.InferredTuple(*subtypes)

    #return lists
    if is_bracketed(text,'[]'):
        text = text[1:-1]
        return inferred_types.InferredList(read_type(text))

    #return sets/dicts
    if is_bracketed(text,'{}'):
        text = text[1:-1]
        parts = split_on(text,':')
        if len(parts)>1:
            return inferred_types.InferredDict([read_type(parts[0])], [read_type(parts[1])])
        else:
            return inferred_types.InferredSet(read_type(text))
    
    type_name = '<{}>'.format(text.strip())
    return builtins.get_built_in_type(type_name)
    
def read_function(text):
    pattern = r"""(?x)
                  ^(?P<fname>\w+) \s*    # function name
                  \( (?P<args>.*) \)   # arguments
                  \s* -> \s*           # arrow
                  (?P<retval>.*)    # return value"""
    results = re.search(pattern, text)
    if results:
        return functions.FunctionType(name=results.group('fname'),
                                      args=[x.strip() for x in results.group('args').split(',')],
                                      returns=read_type(results.group('retval')),
                                      docstring='')
    return None
    
def read_spec(text):
    pass

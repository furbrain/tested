#!/usr/bin/python3
import inspect
import builtins

def print_items(obj, indent=0):
    if indent>12: return
    blanks = " "*indent
    for item, value in inspect.getmembers(obj):
        if item=="__class__": continue
        try:
            print(blanks+"{0} ({1}): None".format(item, ', '.join(inspect.getargspec(value).args)))
            continue
        except TypeError:
            pass
        if inspect.isclass(value):
            print(blanks+"Class: {0}".format(item))
            print_items(value,indent+4)
        else:
            print(blanks+"Builtin: {0}".format(item))

print_items(builtins)


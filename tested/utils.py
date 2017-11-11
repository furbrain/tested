# various utility functions
import ast

def is_ast_sequence(node):
    return (type(node).__name__ in ("Tuple", "List"))

def is_ast_starred(node):
    return type(node).__name__ == "Starred"

def is_ast_node(node):
    return isinstance(node, ast.AST)

def do_not_recurse(default):
    """decorator to prevent inappropriate recursion"""
    def decorator(func):
        def inner(*args):
            hashed_args = [hash(x) for x in args]
            if hasattr(func,'arg_list'):
                if hashed_args in func.arg_list:
                    return default
            else:
                func.arg_list = []
            func.arg_list.append(hashed_args)
            result = func(*args)
            if hasattr(func,'arg_list'):
                del func.arg_list
            return result
        return inner
    return decorator



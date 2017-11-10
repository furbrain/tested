# various utility functions
import ast
from . import inferred_types

def is_ast_sequence(node):
    return (type(node).__name__ in ("Tuple", "List"))

def is_ast_starred(node):
    return type(node).__name__ == "Starred"

def is_ast_node(node):
    return isinstance(node, ast.AST)
    
def is_inferred_type(node):
    return isinstance(node, (inferred_types.InferredType, inferred_types.TypeSet))

